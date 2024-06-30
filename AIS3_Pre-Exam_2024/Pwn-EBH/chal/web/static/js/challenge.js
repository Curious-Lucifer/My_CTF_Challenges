function setupResultView() {
  document.getElementById('pow-container').style.display = 'none';
  document.getElementById('challenge-container').style.display = 'inline-block';

  document.getElementById('challenge-submit-btn').style.display = 'none';
  document.getElementById('result-container').style.display = 'block'

  var restartBtn = document.getElementById('restart-btn')
  restartBtn.style.display = 'inline-block';
  restartBtn.addEventListener('click', () => {
    fetch('/api/user/restart')
    .then((resp) => {
      if (!resp.ok)
        throw new Error('Network error');
      return resp.json();
    })
    .then((data) => {
      if (data['status'] !== 'success')
        throw new Error(data['error']);
      location.reload();
    })
    .catch((error) => {
      console.error('setupResultView Error : ', error);
    });
  })

  fetch('/api/challenge/get_result')
  .then((resp) => {
    if (!resp.ok)
      throw new Error('Network error');
    return resp.json();
  })
  .then((data) => {
    if (data['status'] !== 'success')
      throw new Error(data['error']);
    document.getElementById('challenge-result').innerHTML = atob(data['result']);
  })
  .catch((error) => {
    console.error('setupResultView Error : ', error);
  });
}


let challengeRunningTimer;
function setupChallengeRunningView(lefttime) {
  document.getElementById('pow-container').style.display = 'none';
  document.getElementById('challenge-container').style.display = 'inline-block';

  var challengeSubmitBtn = document.getElementById('challenge-submit-btn');
  var challengeRunningContainer = document.getElementById('challenge-running-container')
  var challengeRunningCounter = document.getElementById('challenge-running-counter');

  challengeSubmitBtn.style.display = 'none';
  challengeRunningContainer.style.display = 'flex';

  if (challengeRunningTimer !== undefined)
    clearInterval(challengeRunningTimer);
  challengeRunningCounter.innerHTML = lefttime;
  challengeRunningTimer = setInterval(() => {
    lefttime -= 1;
    challengeRunningCounter.innerHTML = lefttime;
    if (lefttime === 0) {
      clearInterval(challengeRunningTimer);
      challengeRunningContainer.style.display = 'none';
      setupResultView();
    }
  }, 1000);
}


function setupUploadChallengeView() {
  document.getElementById('pow-container').style.display = 'none';
  document.getElementById('challenge-container').style.display = 'inline-block';

  var challengeForm = document.getElementById('challenge-form');
  var challengeFileField = document.getElementById('challenge-file');

  challengeFileField.addEventListener('change', () => {
    challengeFileField.classList.remove('form-input-error');
  });

  challengeForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const file = challengeFileField.files[0];
    if (file) {
      const formdata = new FormData();
      formdata.append('file', file);
      setupChallengeRunningView(90);
      fetch('/api/challenge/upload_binary', {
        method: 'POST', 
        body: formdata
      })
      .then((resp) => {
        if (!resp.ok)
          throw new Error('Network error');
        return resp.json();
      })
      .then((data) => {
        if (data['status'] !== 'success')
          throw new Error(data['error']);
      })
      .catch((error) => {
        console.error('initChallengeForm Error : ', error);
      });
    } else {
      challengeFileField.classList.add('form-input-error');
    }
  });
}
