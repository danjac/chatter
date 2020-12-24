import axios from 'axios';

import { Controller } from 'stimulus';

export default class extends Controller {
  submit(event) {
    event.preventDefault();

    const referrer = location.href;
    const method = this.element.getAttribute('method');
    const url = this.element.getAttribute('action');

    const data = new FormData(this.element);

    axios({
      data,
      method,
      url,
    });
  }

  reset() {
    this.element.reset();
  }
}
