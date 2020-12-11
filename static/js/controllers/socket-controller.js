import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['input'];

  static values = {
    url: String,
    component: String,
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
    const { group, type, components } = JSON.parse(event.data);
    const component = components[this.componentValue];
    if (
      component &&
      type === this.typeValue &&
      (!this.hasGroupValue || this.groupValue === group)
    ) {
      this.element.innerHTML = component;
    }
  }
}
