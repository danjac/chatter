import axios from 'axios';
import { visit } from '@hotwired/turbo';
import { Controller } from 'stimulus';

export default class extends Controller {
  static values = {
    confirm: String,
    redirect: String,
    remove: Boolean,
    replace: Boolean,
    url: String,
  };

  get(event) {
    event.preventDefault();
    this.sendAjax('GET');
  }

  post(event) {
    event.preventDefault();
    this.sendAjax('POST');
  }

  put(event) {
    event.preventDefault();
    this.sendAjax('POST');
  }

  delete(event) {
    event.preventDefault();
    this.sendAjax('DELETE');
  }

  async sendAjax(method) {
    if (this.hasConfirmValue && !window.confirm(this.confirmValue)) {
      return;
    }

    const url = this.urlValue || this.element.getAttribute('href');

    const response = await axios({
      headers,
      method,
      url,
    });

    if (this.hasRedirectValue) {
      if (this.redirectValue !== 'none') visit(this.redirectValue);
      return;
    }
  }
}
