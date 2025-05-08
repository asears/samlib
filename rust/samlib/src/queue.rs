use crossbeam::queue::ArrayQueue;
use std::sync::Arc;

/// A multiple-producer multiple-consumer queue implementation
pub struct MPMCQueue<T> {
    inner: Arc<ArrayQueue<T>>,
}

impl<T> MPMCQueue<T> {
    /// Creates a new MPMC queue with the specified capacity
    pub fn new(capacity: usize) -> Self {
        Self {
            inner: Arc::new(ArrayQueue::new(capacity)),
        }
    }

    /// Attempts to push a value into the queue
    /// 
    /// Returns Ok(()) if successful, or Err(value) if the queue is full
    pub fn try_push(&self, value: T) -> Result<(), T> {
        self.inner.push(value)
    }

    /// Attempts to pop a value from the queue
    /// 
    /// Returns Some(value) if successful, or None if the queue is empty
    pub fn try_pop(&self) -> Option<T> {
        self.inner.pop()
    }

    /// Returns the current capacity of the queue
    pub fn capacity(&self) -> usize {
        self.inner.capacity()
    }

    /// Returns true if the queue is empty
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Returns true if the queue is full
    pub fn is_full(&self) -> bool {
        self.inner.is_full()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;

    #[test]
    fn test_basic_operations() {
        let queue = MPMCQueue::new(2);
        assert!(queue.try_push(1).is_ok());
        assert!(queue.try_push(2).is_ok());
        assert!(queue.try_push(3).is_err());
        
        assert_eq!(queue.try_pop(), Some(1));
        assert_eq!(queue.try_pop(), Some(2));
        assert_eq!(queue.try_pop(), None);
    }

    #[test]
    fn test_multiple_producers_consumers() {
        let queue = Arc::new(MPMCQueue::new(100));
        let mut handles = vec![];

        // Spawn producer threads
        for i in 0..4 {
            let queue = Arc::clone(&queue);
            handles.push(thread::spawn(move || {
                for j in 0..25 {
                    let val = i * 100 + j;
                    while queue.try_push(val).is_err() {
                        thread::yield_now();
                    }
                }
            }));
        }

        // Spawn consumer threads
        let mut received = Arc::new(parking_lot::Mutex::new(vec![]));
        for _ in 0..4 {
            let queue = Arc::clone(&queue);
            let received = Arc::clone(&received);
            handles.push(thread::spawn(move || {
                for _ in 0..25 {
                    loop {
                        if let Some(val) = queue.try_pop() {
                            received.lock().push(val);
                            break;
                        }
                        thread::yield_now();
                    }
                }
            }));
        }

        // Wait for all threads
        for handle in handles {
            handle.join().unwrap();
        }

        let received = Arc::try_unwrap(received).unwrap().into_inner();
        assert_eq!(received.len(), 100);
    }
}
