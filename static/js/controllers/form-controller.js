import axios from 'axios';

import { Controller } from 'stimulus';

export default class extends Controller {
  async submit(event) {
    event.preventDefault();

    const referrer = location.href;
    const method = this.element.getAttribute('method');
    const url = this.element.getAttribute('action');

    const data = new FormData(this.element);

    await axios({
      data,
      method,
      url,
    });
    const contentType = response.headers['content-type'];
  }

  reset() {
    this.element.reset();
  }
}
