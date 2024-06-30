function initSection() {
  fetch('/api/user/status')
  .then((resp) => {
    if (!resp.ok)
      throw new Error('Network error');
    return resp.json();
  })
  .then((data) => {
    if (data['status'] !== 'success')
      throw new Error(data['error']);

    if (data['has_result']) {
      setupResultView();
    } else if (data['is_running_challenge']) {
      setupChallengeRunningView(data['lefttime']);
    } else if (data['is_pow_verified']) {
      setupUploadChallengeView();
    } else {
      setupPowView();
    }
  })
  .catch((error) => {
    console.error('initSection Error : ', error);
  });
}

initSection();
