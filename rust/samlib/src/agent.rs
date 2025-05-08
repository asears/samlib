use crate::channel::Channel;
use std::any::Any;
use std::sync::Arc;
use tokio::sync::Mutex;

/// Trait representing a message that can be sent between agents
pub trait Message: Any + Send + Sync {}

/// Base trait for all agents in the system
pub trait Agent: Send + Sync {
    /// Handle an incoming message
    fn handle_message(&self, msg: Box<dyn Message>);
    
    /// Get the agent's channel for receiving messages
    fn get_channel(&self) -> Arc<dyn Channel>;
}

/// A reference-counted wrapper around an agent implementation
pub struct AgentRef {
    inner: Arc<dyn Agent>,
}

impl AgentRef {
    /// Create a new agent reference
    pub fn new<T: Agent + 'static>(agent: T) -> Self {
        Self {
            inner: Arc::new(agent),
        }
    }

    /// Send a message to this agent
    pub async fn send(&self, msg: Box<dyn Message>) -> Result<(), Box<dyn Message>> {
        self.inner.get_channel().send(msg).await
    }
}

/// A base implementation of an agent with common functionality
pub struct BaseAgent {
    channel: Arc<dyn Channel>,
    state: Arc<Mutex<Box<dyn Any + Send>>>,
}

impl BaseAgent {
    /// Create a new base agent with the given channel and initial state
    pub fn new<T: Send + 'static>(
        channel: Arc<dyn Channel>,
        initial_state: T,
    ) -> Self {
        Self {
            channel,
            state: Arc::new(Mutex::new(Box::new(initial_state))),
        }
    }

    /// Get access to the agent's state
    pub async fn with_state<T, F, R>(&self, f: F) -> R 
    where
        T: 'static,
        F: FnOnce(&mut T) -> R,
    {
        let mut state = self.state.lock().await;
        let state = state.downcast_mut::<T>().expect("State type mismatch");
        f(state)
    }
}

impl Agent for BaseAgent {
    fn handle_message(&self, _msg: Box<dyn Message>) {
        // Base implementation does nothing - derived agents should override this
    }

    fn get_channel(&self) -> Arc<dyn Channel> {
        Arc::clone(&self.channel)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::channel::Channel;
    use std::sync::atomic::{AtomicUsize, Ordering};

    #[derive(Default)]
    struct TestMessage(usize);
    impl Message for TestMessage {}

    struct TestChannel {
        received: Arc<AtomicUsize>,
    }

    #[async_trait::async_trait]
    impl Channel for TestChannel {
        async fn send(&self, msg: Box<dyn Message>) -> Result<(), Box<dyn Message>> {
            let msg = msg.downcast::<TestMessage>().unwrap();
            self.received.fetch_add(msg.0, Ordering::SeqCst);
            Ok(())
        }
    }

    #[tokio::test]
    async fn test_base_agent() {
        let counter = Arc::new(AtomicUsize::new(0));
        let channel = Arc::new(TestChannel {
            received: Arc::clone(&counter),
        });
        
        let agent = BaseAgent::new(channel, 0usize);
        let agent_ref = AgentRef::new(agent);

        agent_ref.send(Box::new(TestMessage(42))).await.unwrap();
        assert_eq!(counter.load(Ordering::SeqCst), 42);
    }
}
