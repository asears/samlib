import init, { Environment as WasmEnvironment } from '../wasm/pkg';
import { Agent, Channel, Environment, AgentId, ChannelId, Message } from './types';

export class WasmAgent implements Agent {
  constructor(
    private id: AgentId,
    private environment: WasmEnvironment
  ) {}

  async send(message: Message): Promise<void> {
    return this.environment.agent_send(this.id, message);
  }

  async receive(): Promise<Message> {
    return this.environment.agent_receive(this.id);
  }

  getId(): AgentId {
    return this.id;
  }
}

export class WasmChannel implements Channel {
  constructor(
    private id: ChannelId,
    private environment: WasmEnvironment
  ) {}

  async send(data: any): Promise<void> {
    return this.environment.channel_send(this.id, data);
  }

  async receive(): Promise<any> {
    return this.environment.channel_receive(this.id);
  }

  getId(): ChannelId {
    return this.id;
  }
}

export class SamLibEnvironment implements Environment {
  private wasmEnv: WasmEnvironment;
  private initialized: boolean = false;

  private constructor(wasmEnv: WasmEnvironment) {
    this.wasmEnv = wasmEnv;
    this.initialized = true;
  }

  static async create(): Promise<SamLibEnvironment> {
    await init();
    const wasmEnv = new WasmEnvironment();
    return new SamLibEnvironment(wasmEnv);
  }

  async createAgent(id?: AgentId): Promise<Agent> {
    const agentId = await this.wasmEnv.create_agent(id);
    return new WasmAgent(agentId, this.wasmEnv);
  }

  async createChannel(id?: ChannelId): Promise<Channel> {
    const channelId = await this.wasmEnv.create_channel(id);
    return new WasmChannel(channelId, this.wasmEnv);
  }

  getAgent(id: AgentId): Agent | undefined {
    if (this.wasmEnv.has_agent(id)) {
      return new WasmAgent(id, this.wasmEnv);
    }
    return undefined;
  }

  getChannel(id: ChannelId): Channel | undefined {
    if (this.wasmEnv.has_channel(id)) {
      return new WasmChannel(id, this.wasmEnv);
    }
    return undefined;
  }
}
