import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['input', 'messages'];
  static values = {
    id: String,
    socketUrl: String,
  };

  connect() {
    // Websockets setup
    this.socket = new WebSocket('ws://' + window.location.host + this.socketUrlValue);
    this.socket.onmessage = this.newMessage.bind(this);
  }

  disconnect() {
    console.log('disconnecting...');
    this.socket.close();
    this.socket = null;
  }

  newMessage(event) {
    const { message } = JSON.parse(event.data);
    if (message.room === this.idValue) {
      if (this.hasMessagesTarget) {
        this.messagesTarget.innerHTML = message.messages;
      }
    }
  }

  async submit(event) {
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
