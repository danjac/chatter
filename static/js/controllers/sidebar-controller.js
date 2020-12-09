import { Controller } from 'stimulus';

export default class extends Controller {
  static values = {
    socketUrl: String,
  };

  connect() {
    // Websockets setup
    console.log('ws://' + window.location.host + this.socketUrlValue);
    this.socket = new WebSocket('ws://' + window.location.host + this.socketUrlValue);
    this.socket.onmessage = this.newMessage.bind(this);
  }

  disconnect() {
    console.log('disconnecting...');
    this.socket.close();
    this.socket = null;
  }

  newMessage(event) {
    const { sidebar } = JSON.parse(event.data);
    this.element.innerHTML = sidebar;
  }
}
