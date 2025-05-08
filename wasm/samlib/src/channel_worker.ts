// Channel Worker implementation
let messageQueue: any[] = [];

self.onmessage = (event: MessageEvent) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'send':
      messageQueue.push(data);
      self.postMessage({ type: 'sent' });
      break;
      
    case 'receive':
      const message = messageQueue.shift();
      self.postMessage({ type: 'received', data: message });
      break;
      
    default:
      console.error('Unknown message type:', type);
  }
};
