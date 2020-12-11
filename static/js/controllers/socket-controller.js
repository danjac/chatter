import axios from 'axios';
import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['input'];

  static values = {
    group: String,
    type: String,
    url: String,
    refreshUrl: String,
  };

  connect() {
    // Websockets setup
    this.socket = new WebSocket('ws://' + window.location.host + this.urlValue);
    this.socket.onmessage = this.onMessage.bind(this);
  }

  disconnect() {
    this.socket.close();
    this.socket = null;
  }

  async onMessage(event) {
    const { group, type } = JSON.parse(event.data);
    if (this.typeValue == type && (!this.hasGroupValue || this.groupValue === group)) {
      const response = await axios.get(this.refreshUrlValue);
      this.element.innerHTML = response.data;
    }
  }
}
