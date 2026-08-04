// jsdom implements the layout-free parts of the DOM only, so scroll APIs the
// components legitimately use are missing and surface as unhandled errors
// during tests. Stub them; nothing under test asserts on scroll position.
if (!Element.prototype.scrollTo) {
  Element.prototype.scrollTo = () => {};
}
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = () => {};
}
window.scrollTo = () => {};
