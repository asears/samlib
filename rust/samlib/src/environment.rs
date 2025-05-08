use crate::{Agent, AgentRef};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use std::any::TypeId;

/// The Environment manages agent lifecycle and provides agent lookup functionality
pub struct Environment {
    agents: RwLock<HashMap<String, AgentRef>>,
    type_registry: RwLock<HashMap<TypeId, Vec<String>>>,
}

impl Environment {
    /// Create a new environment
    pub fn new() -> Self {
        Self {
            agents: RwLock::new(HashMap::new()),
            type_registry: RwLock::new(HashMap::new()),
        }
    }

    /// Register an agent with the environment
    pub async fn register_agent<T: Agent + 'static>(&self, name: String, agent: T) -> AgentRef {
        let agent_ref = AgentRef::new(agent);
        let type_id = TypeId::of::<T>();
        
        let mut agents = self.agents.write().await;
        let mut type_registry = self.type_registry.write().await;
        
        agents.insert(name.clone(), agent_ref.clone());
        type_registry.entry(type_id)
            .or_default()
            .push(name);
            
        agent_ref
    }

    /// Look up an agent by name
    pub async fn get_agent(&self, name: &str) -> Option<AgentRef> {
        self.agents.read().await.get(name).cloned()
    }

    /// Find all agents of a specific type
    pub async fn get_agents_by_type<T: 'static>(&self) -> Vec<AgentRef> {
        let type_id = TypeId::of::<T>();
        let type_registry = self.type_registry.read().await;
        let agents = self.agents.read().await;
        
        type_registry.get(&type_id)
            .map(|names| {
                names.iter()
                    .filter_map(|name| agents.get(name).cloned())
                    .collect()
            })
            .unwrap_or_default()
    }
}

impl Default for Environment {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{BaseAgent, Channel, Message};
    use std::sync::Arc;

    struct TestChannel;
    
    #[async_trait::async_trait]
    impl Channel for TestChannel {
        async fn send(&self, msg: Box<dyn std::any::Any + Send + Sync>) -> Result<(), Box<dyn std::any::Any + Send + Sync>> {
            Ok(())
        }
    }

    struct TestAgent {
        base: BaseAgent,
    }

    impl TestAgent {
        fn new() -> Self {
            Self {
                base: BaseAgent::new(Arc::new(TestChannel), ()),
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
    async fn test_environment() {
        let env = Environment::new();
        
        // Register agents
        let agent1 = env.register_agent("agent1".to_string(), TestAgent::new()).await;
        let agent2 = env.register_agent("agent2".to_string(), TestAgent::new()).await;
        
        // Test lookup by name
        assert!(env.get_agent("agent1").await.is_some());
        assert!(env.get_agent("agent2").await.is_some());
        assert!(env.get_agent("nonexistent").await.is_none());
        
        // Test lookup by type
        let typed_agents = env.get_agents_by_type::<TestAgent>().await;
        assert_eq!(typed_agents.len(), 2);
    }
}
