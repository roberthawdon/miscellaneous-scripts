// ==UserScript==
// @name         Squash and Merge Colour Change
// @namespace    https://robertianhawdon.me.uk/
// @version      0.5
// @description  Makes it more obvious you're doing a squash... Стоян!
// @author       Robert Ian Hawdon
// @match        https://github.com/*
// @require      http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js
// @require      https://gist.github.com/raw/2625891/waitForKeyElements.js
// @grant        GM_addStyle
// ==/UserScript==

waitForKeyElements (".btn-group-squash > button.btn", actionFunction);


function actionFunction (jNode) {

    jNode.removeClass ("btn-primary").addClass ("btn-blue");

}