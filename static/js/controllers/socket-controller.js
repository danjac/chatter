import axios from 'axios';
import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['input'];

  static values = {
    url: String,
    fetchUrl: String,
    room: String,
    type: String,
  };

  connect() {
    // Websockets setup
    this.socket = new WebSocket('ws://' + window.location.host + this.urlValue);
    this.socket.onmessage = this.newMessage.bind(this);
  }

  disconnect() {
    this.socket.close();
    this.socket = null;
  }

  async newMessage(event) {
    if (this.hasFetchUrlValue && this.hasTypeValue) {
      const { room, type } = JSON.parse(event.data);
      if (type === this.typeValue && (!this.hasRoomValue || this.roomValue === room)) {
        const response = await axios.get(this.fetchUrlValue);
        this.element.innerHTML = response.data;
      }
    }
  }

  async send(event) {
    event.preventDefault();
    const text = this.inputTarget.value.trim();
    if (text) {
      this.socket.send(
        JSON.stringify({
          text,
        })
      );
      this.inputTarget.value = '';
    }
  }
}
