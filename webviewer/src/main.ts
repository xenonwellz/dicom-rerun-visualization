import { WebViewer } from "@rerun-io/web-viewer";

const rrdUrl = "./session.rrd";
const parentElement = document.body;

const viewer = new WebViewer();
await viewer.start(rrdUrl, parentElement, {});