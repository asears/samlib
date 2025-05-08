use wasm_bindgen::prelude::*;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
pub struct Message {
    sender: String,
    recipient: String,
    payload: JsValue,
}

pub struct Agent {
    id: String,
    mailbox: Vec<Message>,
}

impl Agent {
    pub fn new(id: String) -> Self {
        Self {
            id,
            mailbox: Vec::new(),
        }
    }

    pub fn send(&mut self, message: Message) -> Result<(), JsValue> {
        self.mailbox.push(message);
        Ok(())
    }

    pub fn receive(&mut self) -> Option<Message> {
        self.mailbox.pop()
    }
}
