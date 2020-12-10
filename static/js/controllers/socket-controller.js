import axios from 'axios';
import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['input'];

  static values = {
    url: String,
    fetchUrl: String,
    group: String,
    type: String,
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
    // must match group and type
    // e.g. socket-type-value="chat.message" socket-group-value="room-1234"
    // if matches then should do AJAX fetch to refresh content.
    const { group, type } = JSON.parse(event.data);
    if (type === this.typeValue && (!this.hasGroupValue || this.groupValue === group)) {
      const response = await axios.get(this.fetchUrlValue);
      this.element.innerHTML = response.data;
    }
  }
}
