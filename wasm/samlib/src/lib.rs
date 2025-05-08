use wasm_bindgen::prelude::*;
use web_sys::console;

mod agent;
mod channel;
mod environment;

#[wasm_bindgen]
pub struct Environment {
    agents: std::collections::HashMap<String, agent::Agent>,
    channels: std::collections::HashMap<String, channel::Channel>,
}

#[wasm_bindgen]
impl Environment {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        console::log_1(&"Initializing SamLib WASM Environment".into());
        Self {
            agents: std::collections::HashMap::new(),
            channels: std::collections::HashMap::new(),
        }
    }

    pub fn create_agent(&mut self, id: Option<String>) -> Result<String, JsValue> {
        let agent_id = id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
        let agent = agent::Agent::new(agent_id.clone());
        self.agents.insert(agent_id.clone(), agent);
        Ok(agent_id)
    }

    pub fn create_channel(&mut self, id: Option<String>) -> Result<String, JsValue> {
        let channel_id = id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
        let channel = channel::Channel::new(channel_id.clone());
        self.channels.insert(channel_id.clone(), channel);
        Ok(channel_id)
    }
}
