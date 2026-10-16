/*! Axios is MIT licensed; its notice is bundled as axios-LICENSE.txt. */
import axios from "axios";

/** Shared browser HTTP client using Django's same-origin CSRF cookie/header names.
 * @type {import("axios").AxiosInstance}
 */
export const http = axios.create({
    xsrfCookieName: "csrftoken",
    xsrfHeaderName: "X-CSRFToken",
    timeout: 10000,
});
