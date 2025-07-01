// utils/bpmn_layout.js
// Usage: node bpmn_layout.js input.bpmn output_with_di.bpmn

const fs = require('fs');
const { JSDOM } = require('jsdom');
const BpmnJS = require('bpmn-js/lib/Modeler');

if (process.argv.length < 4) {
    console.error('Usage: node bpmn_layout.js <input.bpmn> <output_with_di.bpmn>');
    process.exit(1);
}

const inputFile = process.argv[2];
const outputFile = process.argv[3];

const xml = fs.readFileSync(inputFile, 'utf-8');

// Fake DOM environment for bpmn-js
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
global.window = dom.window;
global.document = dom.window.document;
global.HTMLElement = dom.window.HTMLElement;
global.XMLHttpRequest = undefined;

dom.window.URL.createObjectURL = function () { return ''; };
dom.window.URL.revokeObjectURL = function () { };

dom.window.requestAnimationFrame = function (cb) { return setTimeout(cb, 0); };
dom.window.cancelAnimationFrame = function (id) { clearTimeout(id); };

dom.window.matchMedia = function () { return { matches: false, addListener: function () { }, removeListener: function () { } }; };

const container = dom.window.document.createElement('div');
const modeler = new BpmnJS({ container });

modeler.importXML(xml, function (err) {
    if (err) {
        console.error('import error:', err);
        process.exit(1);
    }
    modeler.saveXML({ format: true }, function (err, result) {
        if (err) {
            console.error('save error:', err);
            process.exit(1);
        }
        fs.writeFileSync(outputFile, result.xml, 'utf-8');
        process.exit(0);
    });
}); 