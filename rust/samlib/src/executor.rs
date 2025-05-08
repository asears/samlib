use std::future::Future;
use std::pin::Pin;
use tokio::sync::mpsc;
use tokio::task::JoinHandle;
use std::sync::Arc;

type BoxedFuture<T> = Pin<Box<dyn Future<Output = T> + Send>>;
type Task = BoxedFuture<()>;

/// The Executor handles task scheduling and execution
pub struct Executor {
    task_tx: mpsc::UnboundedSender<Task>,
    worker_handles: Vec<JoinHandle<()>>,
}

impl Executor {
    /// Create a new executor with the specified number of worker threads
    pub fn new(num_workers: usize) -> Self {
        let (task_tx, task_rx) = mpsc::unbounded_channel();
        let task_rx = Arc::new(tokio::sync::Mutex::new(task_rx));
        
        let mut worker_handles = Vec::with_capacity(num_workers);
        
        // Spawn worker tasks
        for _ in 0..num_workers {
            let task_rx = task_rx.clone();
            let handle = tokio::spawn(async move {
                loop {
                    let task = {
                        let mut rx = task_rx.lock().await;
                        match rx.recv().await {
                            Some(task) => task,
                            None => break,
                        }
                    };
                    task.await;
                }
            });
            worker_handles.push(handle);
        }
        
        Self {
            task_tx,
            worker_handles,
        }
    }
    
    /// Schedule a task for execution
    pub fn schedule<F>(&self, future: F)
    where
        F: Future<Output = ()> + Send + 'static,
    {
        let _ = self.task_tx.send(Box::pin(future));
    }
    
    /// Shutdown the executor and wait for all tasks to complete
    pub async fn shutdown(self) {
        // Drop sender to signal workers to shutdown
        drop(self.task_tx);
        
        // Wait for all workers to complete
        for handle in self.worker_handles {
            let _ = handle.await;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicUsize, Ordering};
    use tokio::time::{sleep, Duration};

    #[tokio::test]
    async fn test_executor() {
        let counter = Arc::new(AtomicUsize::new(0));
        let executor = Executor::new(4);

        // Schedule some tasks
        for _ in 0..100 {
            let counter = counter.clone();
            executor.schedule(async move {
                counter.fetch_add(1, Ordering::SeqCst);
                sleep(Duration::from_millis(1)).await;
            });
        }

        // Add small delay to allow tasks to complete
        sleep(Duration::from_millis(200)).await;
        
        executor.shutdown().await;
        assert_eq!(counter.load(Ordering::SeqCst), 100);
    }

    #[tokio::test]
    async fn test_concurrent_scheduling() {
        let executor = Arc::new(Executor::new(4));
        let counter = Arc::new(AtomicUsize::new(0));
        let mut handles = Vec::new();

        // Spawn multiple tasks that each schedule more tasks
        for _ in 0..10 {
            let executor = executor.clone();
            let counter = counter.clone();
            
            let handle = tokio::spawn(async move {
                for _ in 0..10 {
                    let counter = counter.clone();
                    executor.schedule(async move {
                        counter.fetch_add(1, Ordering::SeqCst);
                        sleep(Duration::from_millis(1)).await;
                    });
                }
            });
            handles.push(handle);
        }

        // Wait for all spawning tasks to complete
        for handle in handles {
            handle.await.unwrap();
        }

        // Add small delay to allow scheduled tasks to complete
        sleep(Duration::from_millis(200)).await;
        
        Arc::try_unwrap(executor).unwrap().shutdown().await;
        assert_eq!(counter.load(Ordering::SeqCst), 100);
    }
}
