use wasm_bindgen::prelude::*;
use web_sys::Worker;

pub struct Channel {
    id: String,
    buffer: Vec<JsValue>,
    worker: Option<Worker>,
}

impl Channel {
    pub fn new(id: String) -> Self {
        Self {
            id,
            buffer: Vec::new(),
            worker: None,
        }
    }

    pub fn send(&mut self, data: JsValue) -> Result<(), JsValue> {
        self.buffer.push(data);
        Ok(())
    }

    pub fn receive(&mut self) -> Option<JsValue> {
        self.buffer.pop()
    }

    pub fn spawn_worker(&mut self) -> Result<(), JsValue> {
        let worker = Worker::new("./channel_worker.js")?;
        self.worker = Some(worker);
        Ok(())
    }
}
