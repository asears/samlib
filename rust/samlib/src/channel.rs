use std::any::Any;
use async_trait::async_trait;

/// A channel for sending messages between agents
#[async_trait]
pub trait Channel: Send + Sync {
    /// Send a message through the channel
    async fn send(&self, msg: Box<dyn Any + Send + Sync>) -> Result<(), Box<dyn Any + Send + Sync>>;
}

/// A channel implementation using a MPMC queue
pub struct QueueChannel<T> {
    queue: crate::queue::MPMCQueue<T>,
}

impl<T: Send + Sync + 'static> QueueChannel<T> {
    /// Create a new queue-based channel with the specified capacity
    pub fn new(capacity: usize) -> Self {
        Self {
            queue: crate::queue::MPMCQueue::new(capacity),
        }
    }
}

#[async_trait]
impl<T: Send + Sync + 'static> Channel for QueueChannel<T> {
    async fn send(&self, msg: Box<dyn Any + Send + Sync>) -> Result<(), Box<dyn Any + Send + Sync>> {
        match msg.downcast::<T>() {
            Ok(msg) => {
                match self.queue.try_push(*msg) {
                    Ok(()) => Ok(()),
                    Err(value) => Err(Box::new(value)),
                }
            }
            Err(msg) => Err(msg),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::time::{sleep, Duration};

    #[tokio::test]
    async fn test_queue_channel() {
        let channel = QueueChannel::<i32>::new(2);
        
        // Test successful sends
        assert!(channel.send(Box::new(1)).await.is_ok());
        assert!(channel.send(Box::new(2)).await.is_ok());
        
        // Test channel full
        assert!(channel.send(Box::new(3)).await.is_err());
        
        // Test wrong type
        assert!(channel.send(Box::new("wrong type")).await.is_err());
    }

    #[tokio::test]
    async fn test_concurrent_channel() {
        let channel = std::sync::Arc::new(QueueChannel::<i32>::new(100));
        let mut handles = Vec::new();

        // Spawn producer tasks
        for i in 0..5 {
            let channel = channel.clone();
            handles.push(tokio::spawn(async move {
                for j in 0..20 {
                    let value = i * 100 + j;
                    while channel.send(Box::new(value)).await.is_err() {
                        sleep(Duration::from_millis(1)).await;
                    }
                }
            }));
        }

        // Wait for all producers
        for handle in handles {
            handle.await.unwrap();
        }
    }
}
