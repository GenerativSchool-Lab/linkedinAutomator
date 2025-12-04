import { Badge } from './ui/badge'
import { cn } from '@/lib/utils'

interface StatusBadgeProps {
  status: string
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const getVariant = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'connected':
        return 'default'
      case 'pending':
        return 'secondary'
      case 'failed':
      case 'rejected':
        return 'destructive'
      case 'connecting':
        return 'outline'
      default:
        return 'secondary'
    }
  }

  return (
    <Badge variant={getVariant(status)}>
      {status || 'Pending'}
    </Badge>
  )
}




