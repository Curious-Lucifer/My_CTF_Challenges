function setupPowView() {
  document.getElementById('challenge-container').style.display = 'none';
  document.getElementById('pow-container').style.display = 'inline-block';
  setupPowParm();
  setupPowForm();
  setupPowCalculate();
}


let powLefttimeTimer;
function setupPowParm() {
  var powPrefixField = document.getElementById('pow-prefix');
  var powDifficultyField = document.getElementById('pow-difficulty');
  var powLefttimeField = document.getElementById('pow-lefttime');

  fetch('/api/pow/get')
  .then((resp) => {
    if (!resp.ok)
      throw new Error('Network error');
    return resp.json();
  })
  .then((data) => {
    if (data['status'] !== 'success')
      throw new Error(data['error']);
    
    powPrefixField.value = data['prefix'];
    powDifficultyField.value = data['difficulty'];

    var lefttime = data['lefttime']
    if (powLefttimeTimer != undefined)
      clearInterval(powLefttimeTimer);
    powLefttimeField.value = lefttime;
    powLefttimeTimer = setInterval(() => {
      lefttime -= 1;
      powLefttimeField.value = lefttime;
      if (lefttime === 0)
        clearInterval(powLefttimeTimer);
    }, 1000);
  })
  .catch((error) => {
    console.error('getPow Error : ', error);
  });
}


function setupPowForm() {
  var powForm = document.getElementById('pow-form');
  var powAnswerField = document.getElementById('pow-answer');

  powAnswerField.addEventListener('input', () => {
    powAnswerField.classList.remove('form-input-error');
  });

  powForm.addEventListener('submit', (event) => {
    event.preventDefault();
    verifyPow();
  });
}


function setupPowCalculate() {
  var powCalculateBtn = document.getElementById('pow-calculate-btn');
  var powLoadingContainer = document.getElementById('pow-calculate-loading-container');
  var powAnswerField = document.getElementById('pow-answer');

  powCalculateBtn.addEventListener('click', () => {
    powCalculateBtn.style.display = 'none';
    powLoadingContainer.style.display = 'flex';

    var prefix = document.getElementById('pow-prefix').value;
    var difficulty = document.getElementById('pow-difficulty').value;

    var worker = new Worker('/static/js/calculate_pow.js');
    worker.onmessage = (e) => {
      powAnswerField.value = e.data;
      powLoadingContainer.style.display = 'none';
      powCalculateBtn.style.display = 'inline-block';
    };
    worker.postMessage({
      prefix: prefix, 
      difficulty: difficulty
    });
  })
}


function verifyPow() {
  var powAnswerField = document.getElementById('pow-answer');

  if (powAnswerField.value === '') {
    powAnswerField.classList.add('form-input-error');
    return;
  }

  var lefttime = parseInt(document.getElementById('pow-lefttime').value);
  if (isNaN(lefttime) || (lefttime == 0)) {
    setupPowParm();
    return;
  }

  fetch('/api/pow/verify', {
    method: 'POST', 
    headers: {
      'Content-Type': 'application/json'
    }, 
    body: JSON.stringify({
      answer: powAnswerField.value
    })
  })
  .then((resp) => {
    if (!resp.ok)
      throw new Error('Network error');
    return resp.json();
  })
  .then((data) => {
    if (data['status'] !== 'success')
      throw new Error(data['error']);
    
    if (data['result'] === 'verified') {
      setupUploadChallengeView();
    } else if (data['result'] === 'wrong') {
      powAnswerField.classList.add('form-input-error');
    } else {
      setupPowParm();
    }
  })
  .catch((error) => {
    console.error('verifyPow Error : ', error);
  });
}
