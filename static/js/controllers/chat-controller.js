import axios from 'axios';
import { Controller } from 'stimulus';
import ReconnectingWebSocket from 'reconnecting-websocket';

import { connectStreamSource, disconnectStreamSource } from '@hotwired/turbo';

export default class extends Controller {
  static targets = ['input'];

  static values = {
    socketUrl: String,
    sendUrl: String,
  };

  connect() {
    this.source = new ReconnectingWebSocket(this.socketUrlValue);
    // this.source = new WebSocket(this.socketUrlValue);
    connectStreamSource(this.source);
  }

  disconnect() {
    disconnectStreamSource(this.source);
    this.source = null;
  }

  async sendMessage(event) {
    event.preventDefault();
    const msg = this.inputTarget.value.trim();
    if (msg) {
      const data = new FormData();
      data.append('text', msg);
      await axios({
        data,
        method: 'post',
        url: this.sendUrlValue,
      });
    }
    this.inputTarget.value = '';
  }
}
