function boldContent() {
    let txtarea = document.getElementById("editor-text");
    let currentVal = txtarea.value;
    console.log(currentVal);
    // obtain the object reference for the <textarea>
    const start = txtarea.selectionStart;
    const end = txtarea.selectionEnd;
    console.log(start + ' ' + end)
    //Make sure a selection was made
    if (start === end) {
        return;
    }
    const selectedText = txtarea.value.substring(start, end);
    //Find most recent bold to left
    const leftBold = currentVal.slice(0, start).lastIndexOf("**")
    //Find most recent bold to right
    const rightBold = currentVal.slice(end).indexOf("**");
    console.log(leftBold);
    console.log(rightBold);
    //Want to unbold
    if (leftBold === start - 2 && rightBold === 0) {
        currentVal = currentVal.slice(0, start - 2) + selectedText + currentVal.slice(end + 2);
    }
    else {
        currentVal = currentVal.slice(0, start) + "**" + selectedText + "**" + currentVal.slice(end);
    }
    txtarea.value = currentVal;
}