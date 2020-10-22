function formatSeconds(value) {
    let theTime = parseInt(value);
    let middle = 0;
    let hour = 0;
    if (theTime > 60) {
      middle = parseInt(theTime / 60);
      theTime = parseInt(theTime % 60);
      if (middle > 60) {
        hour = parseInt(middle / 60);
        middle = parseInt(middle % 60);
      }
    }
    let result = "" + parseInt(theTime) + "秒";
    if (middle > 0) {
      result = "" + parseInt(middle) + "分" + result;
    }
    if (hour > 0) {
      result = "" + parseInt(hour) + "时" + result;
    }
    return result;
}
export default {formatSeconds}