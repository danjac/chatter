import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['input'];

  static values = {
    url: String,
    fragment: String,
  };

  connect() {
    // Websockets setup
    this.socket = new WebSocket('ws://' + window.location.host + this.urlValue);
    this.socket.onmessage = this.newMessage.bind(this);

    console.log(this.element, this.fragmentValue);
  }

  disconnect() {
    console.log('disconnecting...');
    this.socket.close();
    this.socket = null;
  }

  newMessage(event) {
    if (this.hasFragmentValue) {
      const { fragments } = JSON.parse(event.data);
      if (fragments[this.fragmentValue]) {
        this.element.innerHTML = fragments[this.fragmentValue];
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
