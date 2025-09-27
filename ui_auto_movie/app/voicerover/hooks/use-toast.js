import toast from 'react-hot-toast';

export function useToast() {
  return {
    toast: (options) => {
      if (typeof options === 'string') {
        return toast(options);
      }
      
      const { title, description, variant = 'default' } = options;
      const message = description ? `${title}: ${description}` : title;
      
      switch (variant) {
        case 'destructive':
          return toast.error(message);
        case 'success':
          return toast.success(message);
        default:
          return toast(message);
      }
    }
  };
}
