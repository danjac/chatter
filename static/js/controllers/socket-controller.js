import { Controller } from 'stimulus';
import { connectStreamSource, disconnectStreamSource } from '@hotwired/turbo';
export default class extends Controller {
  static values = {
    url: String,
  };

  connect() {
    console.log('connecting event source at', this.urlValue);
    this.source = new WebSocket(this.urlValue);
    connectStreamSource(this.source);
  }

  disconnect() {
    disconnectStreamSource(this.source);
    this.source = null;
  }
}
