import { API_ENDPOINTS } from '../api/endpoints';
import apiClient from '../api/client';
import { UserProfile, User } from '../types/models';
import storageService from './storageService';

export interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  phone?: string;
  preferred_language?: 'fr' | 'mg';
  profile_picture?: string;
}

export interface UpdateProfileResponse {
  success: boolean;
  user: User;
  message?: string;
}

class UserProfileService {
  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    try {
      const response = await apiClient.get<UserProfile>(API_ENDPOINTS.USERS.PROFILE);
      return response.data;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(data: UpdateProfileData): Promise<UpdateProfileResponse> {
    try {
      // Create FormData for multipart upload if profile picture is included
      let requestData: FormData | UpdateProfileData = data;
      
      if (data.profile_picture) {
        const formData = new FormData();
        
        // Add text fields
        if (data.first_name) formData.append('first_name', data.first_name);
        if (data.last_name) formData.append('last_name', data.last_name);
        if (data.phone) formData.append('phone', data.phone);
        if (data.preferred_language) formData.append('preferred_language', data.preferred_language);
        
        // Add profile picture file
        if (data.profile_picture.startsWith('file://')) {
          // Local file path
          const filename = data.profile_picture.split('/').pop() || 'profile.jpg';
          const match = filename.match(/\.([^.]+)$/);
          const fileType = match ? `image/${match[1]}` : 'image/jpeg';
          
          formData.append('profile_picture', {
            uri: data.profile_picture,
            name: filename,
            type: fileType,
          } as any);
        } else if (data.profile_picture.startsWith('data:')) {
          // Base64 data
          const base64Data = data.profile_picture.split(',')[1];
          const filename = 'profile.jpg';
          
          formData.append('profile_picture', {
            uri: data.profile_picture,
            name: filename,
            type: 'image/jpeg',
          } as any);
        }
        
        requestData = formData;
      }

      const response = await apiClient.put(
        API_ENDPOINTS.USERS.ME,
        requestData,
        data.profile_picture ? {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        } : {}
      );

      // Update stored user data if successful
      if (response.data.user) {
        await storageService.secureSet('user', JSON.stringify(response.data.user));
      }

      return {
        success: true,
        user: response.data.user,
        message: response.data.message || 'Profile updated successfully',
      };
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences: {
    preferred_language?: 'fr' | 'mg';
    notifications_enabled?: boolean;
    biometric_enabled?: boolean;
  }): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await apiClient.put(API_ENDPOINTS.USERS.ME, preferences);
      return {
        success: true,
        message: response.data.message || 'Preferences updated successfully',
      };
    } catch (error) {
      console.error('Error updating preferences:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Upload profile picture
   */
  async uploadProfilePicture(imageUri: string): Promise<{ profile_picture_url: string }> {
    try {
      const formData = new FormData();
      
      // Determine filename and type
      const filename = imageUri.split('/').pop() || 'profile.jpg';
      const match = filename.match(/\.([^.]+)$/);
      const fileType = match ? `image/${match[1]}` : 'image/jpeg';
      
      formData.append('profile_picture', {
        uri: imageUri,
        name: filename,
        type: fileType,
      } as any);

      const response = await apiClient.put(
        API_ENDPOINTS.USERS.ME,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return {
        profile_picture_url: response.data.profile_picture_url,
      };
    } catch (error) {
      console.error('Error uploading profile picture:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Handle API errors
   */
  private handleError(error: any): Error {
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          return new Error(data.message || 'Invalid data provided');
        case 401:
          return new Error('Authentication required');
        case 403:
          return new Error('Access denied');
        case 404:
          return new Error('User profile not found');
        case 422:
          return new Error(data.message || 'Validation error');
        case 500:
          return new Error('Server error. Please try again later');
        default:
          return new Error(data.message || 'An error occurred');
      }
    } else if (error.request) {
      return new Error('Network error. Please check your connection');
    } else {
      return new Error('An unexpected error occurred');
    }
  }
}

export const userProfileService = new UserProfileService();