import { DATE_FORMATS } from '../constants/app.constants';

export const formatCurrency = (amount: number, currency: string = 'MGA'): string => {
  return new Intl.NumberFormat('mg-MG', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatDate = (date: Date | string, format: string = DATE_FORMATS.DISPLAY): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return 'Invalid Date';
  }
  
  return dateObj.toLocaleString('mg-MG', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDateOnly = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return 'Invalid Date';
  }
  
  return dateObj.toLocaleDateString('mg-MG', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

export const formatTimeOnly = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return 'Invalid Time';
  }
  
  return dateObj.toLocaleTimeString('mg-MG', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatBadgeId = (badgeId: string): string => {
  // Format badge ID with spaces for better readability
  if (badgeId.length >= 8) {
    return badgeId.replace(/(\w{4})(\w+)/, '$1 $2');
  }
  return badgeId;
};

export const formatLicensePlate = (plate: string): string => {
  // Format license plate with spaces
  // Example: XX1234XX -> XX 1234 XX
  const cleaned = plate.replace(/\s/g, '');
  
  if (cleaned.length === 8) {
    // Format: XX1234XX -> XX 1234 XX
    return cleaned.replace(/(\w{2})(\d{4})(\w{2})/, '$1 $2 $3');
  } else if (cleaned.length === 10) {
    // Format: 1234XX12 -> 1234 XX 12
    return cleaned.replace(/(\d{4})(\w{2})(\d{2})/, '$1 $2 $3');
  }
  
  return cleaned;
};

export const formatPhoneNumber = (phone: string): string => {
  // Format Malagasy phone number
  const cleaned = phone.replace(/\s/g, '');
  
  if (cleaned.startsWith('+261')) {
    // +261 XX XX XXX XX
    const local = cleaned.substring(4);
    if (local.length === 9) {
      return `+261 ${local.substring(0, 2)} ${local.substring(2, 4)} ${local.substring(4, 7)} ${local.substring(7)}`;
    }
  } else if (cleaned.startsWith('0')) {
    // 0X XX XXX XX
    if (cleaned.length === 10) {
      return `${cleaned.substring(0, 2)} ${cleaned.substring(2, 4)} ${cleaned.substring(4, 7)} ${cleaned.substring(7)}`;
    }
  }
  
  return phone;
};

export const formatAgentType = (agentType: string): string => {
  switch (agentType) {
    case 'agent_government':
      return 'Agent Gouvernemental';
    case 'agent_partenaire':
      return 'Agent Partenaire';
    default:
      return 'Agent';
  }
};

export const formatValidationStatus = (status: string): string => {
  switch (status) {
    case 'valid':
      return 'Valide';
    case 'invalid':
      return 'Invalide';
    case 'expired':
      return 'Expiré';
    case 'pending':
      return 'En attente';
    default:
      return status;
  }
};

export const formatPaymentStatus = (status: string): string => {
  switch (status) {
    case 'paid':
      return 'Payé';
    case 'pending':
      return 'En attente';
    case 'failed':
      return 'Échoué';
    case 'expired':
      return 'Expiré';
    default:
      return status;
  }
};

export const formatPaymentMethod = (method: string): string => {
  switch (method) {
    case 'cash':
      return 'Espèces';
    case 'mvola':
      return 'Mvola';
    case 'card':
      return 'Carte';
    default:
      return method;
  }
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
};

export const capitalizeFirst = (text: string): string => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};