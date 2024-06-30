importScripts('https://cdnjs.cloudflare.com/ajax/libs/sjcl/1.0.8/sjcl.min.js');


function pow(prefix, difficulty) {
  let zeros = '0'.repeat(difficulty);
  let isValid = (hexdigest) => {
    let bin = '';
    for (let c of hexdigest)
      bin += parseInt(c, 16).toString(2).padStart(4, '0');
    return bin.startsWith(zeros);
  }
  let i = 0;
  while (true) {
    let hexdigest = sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(prefix + i.toString()));
    if (isValid(hexdigest)) {
      return i;
    }
    i++;
  }
}


self.onmessage = (e) => {
  var prefix = e.data.prefix;
  var difficulty = e.data.difficulty;
  var answer = pow(prefix, difficulty);
  self.postMessage(answer);
};