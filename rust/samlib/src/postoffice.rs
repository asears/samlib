use crate::{Agent, AgentRef, Message};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

/// PostOffice handles message routing between agents
pub struct PostOffice {
    routes: RwLock<HashMap<String, AgentRef>>,
}

impl PostOffice {
    /// Create a new PostOffice instance
    pub fn new() -> Self {
        Self {
            routes: RwLock::new(HashMap::new()),
        }
    }

    /// Register an agent with the post office
    pub async fn register(&self, address: String, agent: AgentRef) {
        self.routes.write().await.insert(address, agent);
    }

    /// Remove an agent from the post office
    pub async fn unregister(&self, address: &str) {
        self.routes.write().await.remove(address);
    }

    /// Send a message to a specific agent
    pub async fn send_to(&self, address: &str, message: Box<dyn Message>) -> Result<(), Box<dyn Message>> {
        if let Some(agent) = self.routes.read().await.get(address) {
            agent.send(message).await
        } else {
            Err(message)
        }
    }

    /// Broadcast a message to all registered agents
    pub async fn broadcast(&self, message: Box<dyn Message + Clone>) {
        let routes = self.routes.read().await;
        for agent in routes.values() {
            let _ = agent.send(message.clone()).await;
        }
    }
}

impl Default for PostOffice {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{BaseAgent, Channel};
    use std::sync::atomic::{AtomicUsize, Ordering};

    #[derive(Clone)]
    struct TestMessage(usize);
    impl Message for TestMessage {}

    struct TestChannel {
        counter: Arc<AtomicUsize>,
    }

    #[async_trait::async_trait]
    impl Channel for TestChannel {
        async fn send(&self, msg: Box<dyn std::any::Any + Send + Sync>) -> Result<(), Box<dyn std::any::Any + Send + Sync>> {
            if let Ok(msg) = msg.downcast::<TestMessage>() {
                self.counter.fetch_add(msg.0, Ordering::SeqCst);
                Ok(())
            } else {
                Err(msg)
            }
        }
    }

    struct TestAgent {
        base: BaseAgent,
    }

    impl TestAgent {
        fn new(counter: Arc<AtomicUsize>) -> Self {
            Self {
                base: BaseAgent::new(Arc::new(TestChannel { counter }), ()),
            }
        }
    }

    impl Agent for TestAgent {
        fn handle_message(&self, _msg: Box<dyn Message>) {}
        
        fn get_channel(&self) -> Arc<dyn Channel> {
            self.base.get_channel()
        }
    }

    #[tokio::test]
    async fn test_post_office() {
        let post_office = PostOffice::new();
        let counter1 = Arc::new(AtomicUsize::new(0));
        let counter2 = Arc::new(AtomicUsize::new(0));

        // Register agents
        let agent1 = AgentRef::new(TestAgent::new(counter1.clone()));
        let agent2 = AgentRef::new(TestAgent::new(counter2.clone()));
        
        post_office.register("agent1".to_string(), agent1).await;
        post_office.register("agent2".to_string(), agent2).await;

        // Test direct message
        post_office.send_to("agent1", Box::new(TestMessage(42))).await.unwrap();
        assert_eq!(counter1.load(Ordering::SeqCst), 42);
        assert_eq!(counter2.load(Ordering::SeqCst), 0);

        // Test broadcast
        post_office.broadcast(Box::new(TestMessage(10))).await;
        assert_eq!(counter1.load(Ordering::SeqCst), 52);
        assert_eq!(counter2.load(Ordering::SeqCst), 10);

        // Test unregister
        post_office.unregister("agent1").await;
        assert!(post_office.send_to("agent1", Box::new(TestMessage(1))).await.is_err());
    }
}
