// composables/useInfiniteScroll.js
import { ref, computed, watch, onBeforeUnmount } from "vue";

export function useInfiniteScroll(sourceData, pageSize = 20) {
  const visibleCount = ref(pageSize);
  let observer = null;

  const visibleData = computed(() => sourceData.value.slice(0, visibleCount.value));
  const hasMore = computed(() => visibleCount.value < sourceData.value.length);

  const loadMore = () => {
    if (!hasMore.value) return;
    visibleCount.value += pageSize;
  };

  // whenever filters/sort change the underlying result, start over from page 1
  watch(sourceData, () => {
    visibleCount.value = pageSize;
  });

  // function ref: re-attaches the observer correctly even if the sentinel
  // element gets added/removed by v-if (e.g. loading states)
  const setSentinel = (el) => {
    observer?.disconnect();
    if (!el) return;
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) loadMore();
      },
      { rootMargin: "200px" }
    );
    observer.observe(el);
  };

  onBeforeUnmount(() => observer?.disconnect());

  return { visibleData, hasMore, setSentinel };
}