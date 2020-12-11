import { Controller } from 'stimulus';

export default class extends Controller {
  static targets = ['input'];

  static values = {
    url: String,
    component: String,
    include: String,
    exclude: String,
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

  getComponent(group, type, components) {
    const component = components[this.componentValue];
    if (!component) {
      return null;
    }
    if (type !== this.typeValue) {
      return null;
    }
    if (!group) {
      return component;
    }

    console.log(group, this.includeValue, this.excludeValue);

    if (this.hasIncludeValue && group === this.includeValue) {
      return component;
    }

    if (this.hasExcludeValue && group !== this.excludeValue) {
      return component;
    }

    return null;
  }

  async onMessage(event) {
    const { group, type, components } = JSON.parse(event.data);
    const component = this.getComponent(group, type, components);
    if (component) {
      this.element.innerHTML = component;
    }
  }
}
