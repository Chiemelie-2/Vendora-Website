/**
 * Handles the Profile Photo Modal and Real-time Preview
 */
document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('photoModal');
  const fileInput = document.getElementById('id_profile_image');
  const openBtn = document.getElementById('open-modal-btn');
  const updatePhotoBtn = document.getElementById('update-photo-btn');
  const cancelBtn = document.getElementById('cancel-modal-btn'); // btn-cancel-modal

  // 1. Open modal when clicking the avatar circle
  if (openBtn) {
    openBtn.addEventListener('click', function () {
      modal.style.display = 'flex';
    });
  }

  // 2. "Update Photo" triggers the hidden file input
  if (updatePhotoBtn) {
    updatePhotoBtn.addEventListener('click', function () {
      if (fileInput) fileInput.click();
    });
  }

  // 3. Cancel closes the modal
  if (cancelBtn) {
    cancelBtn.addEventListener('click', function () {
      modal.style.display = 'none';
    });
  }

  // 4. When a file is selected — preview immediately and close modal
  if (fileInput) {
    fileInput.addEventListener('change', function () {
      if (this.files && this.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
          const container = document.querySelector('.profile-avatar-container');
          // Try to find an existing <img> with id="preview-image"
          let previewEl = document.getElementById('preview-image');

          if (previewEl && previewEl.tagName === 'IMG') {
            // Already an <img> — just update src
            previewEl.src = e.target.result;
          } else {
            // Was a placeholder div — replace it with a real <img>
            const newImg = document.createElement('img');
            newImg.src = e.target.result;
            newImg.className = 'avatar-img';
            newImg.id = 'preview-image';
            newImg.alt = 'Profile photo';
            if (previewEl) {
              previewEl.replaceWith(newImg);
            } else {
              // Fallback: prepend to container
              container.insertBefore(newImg, container.firstChild);
            }
          }
        };

        reader.readAsDataURL(this.files[0]);

        // Close modal after selection
        modal.style.display = 'none';
      }
    });
  }

  // 5. Click outside the modal box to close
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        modal.style.display = 'none';
      }
    });
  }
});