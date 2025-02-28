from django.contrib import messages
from apps.user.forms import CoverImageForm, ProfileImageForm, UpdatePersonalInfoForm

def update_personal_information(request, user):
  personal_info_form = UpdatePersonalInfoForm(request.POST, instance=user)
  profile_form = ProfileImageForm(request.POST, request.FILES, instance=user)
  cover_form = CoverImageForm(request.POST, request.FILES, instance=user)

  # Flags to track if forms have been successfully updated
  personal_info_updated = False
  profile_image_updated = False
  cover_image_updated = False

  # Track if any errors occur
  personal_info_error = False
  profile_image_error = False
  cover_image_error = False

  # Update Personal Information if form data has changed
  if personal_info_form.has_changed():
    if personal_info_form.is_valid():
      personal_info_form.save()
      personal_info_updated = True
    else:
      personal_info_error = True
          
  # Update Profile Image if a file has been uploaded
  if any(request.FILES.get(key) for key in profile_form.fields):
    if profile_form.is_valid():
      profile_form.save()
      profile_image_updated = True
    else:
      profile_image_error = True
          
  # Update Cover Image if a file has been uploaded
  if any(request.FILES.get(key) for key in cover_form.fields):
    if cover_form.is_valid():
      cover_form.save()
      cover_image_updated = True
    else:
      cover_image_error = True

  # Check if all forms were updated successfully
  all_updated = personal_info_updated and profile_image_updated and cover_image_updated
  all_success = not (personal_info_error or profile_image_error or cover_image_error)

  # Show messages based on update status
  if all_updated and all_success:
    messages.success(request, "Personal information updated successfully.")
  else:
    if personal_info_updated and not personal_info_error:
      messages.success(request, "Personal information updated successfully!")
      
    if personal_info_error:
      messages.error(request, "Error updating personal information.")
              
    if profile_image_updated and not profile_image_error:
      messages.success(request, "Profile image uploaded successfully!")

    if profile_image_error:
      messages.error(request, "Error uploading profile image.")
              
    if cover_image_updated and not cover_image_error:
      messages.success(request, "Cover image uploaded successfully!")

    if cover_image_error:
      messages.error(request, "Error uploading cover image.")
 
    if not (personal_info_updated or profile_image_updated or cover_image_updated):
      messages.info(request, "No updates were made.")