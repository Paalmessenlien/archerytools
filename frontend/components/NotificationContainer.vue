<template>
  <div class="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
    <TransitionGroup name="notifications" tag="div">
      <NotificationToast
        v-for="notification in notifications"
        :key="notification.id"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :duration="0"
        :persistent="true"
        class="pointer-events-auto"
        @close="removeNotification(notification.id)"
      />
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useNotifications } from '~/composables/useNotifications'

const { notifications, removeNotification } = useNotifications()
</script>

<style scoped>
.notifications-move,
.notifications-enter-active,
.notifications-leave-active {
  transition: all 0.3s ease;
}

.notifications-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notifications-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notifications-leave-active {
  position: absolute;
  right: 0;
}
</style>