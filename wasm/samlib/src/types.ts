/**
 * Core types for the SamLib WASM implementation
 */

export type AgentId = string;
export type ChannelId = string;

export interface Message {
  sender: AgentId;
  recipient: AgentId;
  payload: any;
}

export interface Agent {
  id: AgentId;
  send(message: Message): Promise<void>;
  receive(): Promise<Message>;
}

export interface Channel {
  id: ChannelId;
  send(data: any): Promise<void>;
  receive(): Promise<any>;
}

export interface Environment {
  createAgent(id?: AgentId): Promise<Agent>;
  createChannel(id?: ChannelId): Promise<Channel>;
  getAgent(id: AgentId): Agent | undefined;
  getChannel(id: ChannelId): Channel | undefined;
}
