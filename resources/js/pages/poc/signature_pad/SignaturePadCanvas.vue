<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import SignaturePad from 'signature_pad';
import type { PointGroup } from 'signature_pad';
import { useResizeObserver } from '@vueuse/core';
import { RotateCcw, RotateCw, Trash2, PenTool } from '@lucide/vue';

interface Props {
  modelValue?: string | null;
  penColor?: string;
  backgroundColor?: string;
  minWidth?: number;
  maxWidth?: number;
  disabled?: boolean;
  showToolbar?: boolean;
  showHelperLine?: boolean;
  placeholderText?: string;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  penColor: '#0f172a',
  backgroundColor: 'rgba(255, 255, 255, 0)',
  minWidth: 1.5,
  maxWidth: 3.5,
  disabled: false,
  showToolbar: true,
  showHelperLine: true,
  placeholderText: 'เซ็นลายเซ็นของคุณภายในกรอบนี้ (รองรับ ปากกา Stylus, นิ้วสัมผัส, เมาส์)',
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | null): void;
  (e: 'change', isEmpty: boolean): void;
  (e: 'strokeEnd', payload: { dataUrl: string | null; isEmpty: boolean; pointGroups: PointGroup[] }): void;
}>();

const canvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);

let padInstance: SignaturePad | null = null;
const redoStack = ref<PointGroup[]>([]);
const hasDrawn = ref(false);

const resizeCanvas = () => {
  const canvas = canvasRef.value;
  const container = containerRef.value;
  if (!canvas || !container || !padInstance) return;

  const rect = container.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) return;

  const ratio = Math.max(window.devicePixelRatio || 1, 1);
  const existingData = padInstance.toData();

  canvas.width = rect.width * ratio;
  canvas.height = rect.height * ratio;
  canvas.style.width = `${rect.width}px`;
  canvas.style.height = `${rect.height}px`;

  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.scale(ratio, ratio);
  }

  padInstance.clear();
  if (existingData && existingData.length > 0) {
    padInstance.fromData(existingData);
  }
};

const handleStrokeEnd = () => {
  if (!padInstance) return;
  const empty = padInstance.isEmpty();
  hasDrawn.value = !empty;
  redoStack.value = []; // Clear redo stack on new stroke

  const currentDataUrl = empty ? null : padInstance.toDataURL('image/png');
  emit('update:modelValue', currentDataUrl);
  emit('change', empty);
  emit('strokeEnd', {
    dataUrl: currentDataUrl,
    isEmpty: empty,
    pointGroups: padInstance.toData(),
  });
};

onMounted(() => {
  nextTick(() => {
    if (!canvasRef.value) return;

    padInstance = new SignaturePad(canvasRef.value, {
      penColor: props.penColor,
      backgroundColor: props.backgroundColor,
      minWidth: props.minWidth,
      maxWidth: props.maxWidth,
      throttle: 0,
    });

    resizeCanvas();

    padInstance.addEventListener('endStroke', handleStrokeEnd);

    if (props.disabled) {
      padInstance.off();
    }
  });
});

useResizeObserver(containerRef, () => {
  resizeCanvas();
});

watch(
  () => props.penColor,
  (newColor) => {
    if (padInstance && newColor) {
      padInstance.penColor = newColor;
    }
  }
);

watch(
  () => [props.minWidth, props.maxWidth],
  ([newMin, newMax]) => {
    if (padInstance) {
      padInstance.minWidth = newMin;
      padInstance.maxWidth = newMax;
    }
  }
);

watch(
  () => props.disabled,
  (isDisabled) => {
    if (!padInstance) return;
    if (isDisabled) {
      padInstance.off();
    } else {
      padInstance.on();
    }
  }
);

onBeforeUnmount(() => {
  padInstance?.off();
});

const clear = () => {
  if (!padInstance) return;
  padInstance.clear();
  redoStack.value = [];
  hasDrawn.value = false;
  emit('update:modelValue', null);
  emit('change', true);
  emit('strokeEnd', {
    dataUrl: null,
    isEmpty: true,
    pointGroups: [],
  });
};

const undo = () => {
  if (!padInstance) return;
  const data = padInstance.toData();
  if (data.length > 0) {
    const removedStroke = data.pop();
    if (removedStroke) {
      redoStack.value.push(removedStroke);
    }
    padInstance.fromData(data);
    handleStrokeEnd();
  }
};

const redo = () => {
  if (!padInstance || redoStack.value.length === 0) return;
  const strokeToRestore = redoStack.value.pop();
  if (strokeToRestore) {
    const data = padInstance.toData();
    data.push(strokeToRestore);
    padInstance.fromData(data);
    handleStrokeEnd();
  }
};

const toDataURL = (type = 'image/png', quality?: number): string | null => {
  if (!padInstance || padInstance.isEmpty()) return null;
  return padInstance.toDataURL(type, quality);
};

const toSVG = (): string | null => {
  if (!padInstance || padInstance.isEmpty()) return null;
  return padInstance.toSVG();
};

const toBlob = async (type = 'image/png'): Promise<Blob | null> => {
  return new Promise((resolve) => {
    if (!canvasRef.value || padInstance?.isEmpty()) {
      resolve(null);
      return;
    }
    canvasRef.value.toBlob(resolve, type);
  });
};

const toData = (): PointGroup[] => {
  return padInstance?.toData() || [];
};

const fromData = (pointGroups: PointGroup[]) => {
  if (!padInstance) return;
  padInstance.fromData(pointGroups);
  handleStrokeEnd();
};

const isEmpty = (): boolean => {
  return padInstance?.isEmpty() ?? true;
};

defineExpose({
  clear,
  undo,
  redo,
  toDataURL,
  toSVG,
  toBlob,
  toData,
  fromData,
  isEmpty,
  canUndo: () => (padInstance ? padInstance.toData().length > 0 : false),
  canRedo: () => redoStack.value.length > 0,
});
</script>

<template>
  <div class="flex flex-col gap-2.5 w-full select-none">
    <!-- Signature Canvas Container -->
    <div
      ref="containerRef"
      class="relative w-full h-64 sm:h-72 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 overflow-hidden shadow-xs transition-colors focus-within:border-primary/80"
      :class="{ 'opacity-60 pointer-events-none': disabled }"
    >
      <canvas
        ref="canvasRef"
        class="block w-full h-full cursor-crosshair touch-none select-none"
        style="touch-action: none;"
      ></canvas>

      <!-- Signature Guide Line & Hint -->
      <div
        v-if="showHelperLine"
        class="pointer-events-none absolute bottom-8 left-8 right-8 border-b border-slate-300 dark:border-slate-700 flex items-center justify-between pb-1.5 text-xs text-slate-400 dark:text-slate-500"
      >
        <span class="flex items-center gap-1.5 font-medium">
          <PenTool class="w-3.5 h-3.5 text-primary" />
          {{ placeholderText }}
        </span>
        <span class="text-[11px] font-mono opacity-70">✕ วางลายเซ็นบนเส้น</span>
      </div>

      <!-- Watermark Badge for Tablet/Mobile Device Status -->
      <div class="pointer-events-none absolute top-3 right-3 flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-slate-100/90 dark:bg-slate-900/90 text-[10px] font-mono text-slate-500 border border-slate-200 dark:border-slate-800 backdrop-blur-xs">
        <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
        PointerEvents Active
      </div>
    </div>

    <!-- Built-in Toolbar (Optional) -->
    <div v-if="showToolbar" class="flex flex-wrap items-center justify-between gap-2 text-xs">
      <div class="text-slate-500 dark:text-slate-400 text-[11px] flex items-center gap-1.5">
        <span class="inline-flex items-center px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] font-medium text-slate-600 dark:text-slate-300">
          HiDPI Retina
        </span>
        <span>ป้องกันจอเลื่อนบนมือถืออัตโนมัติ (touch-action: none)</span>
      </div>

      <div class="flex items-center gap-1.5">
        <button
          type="button"
          @click="undo"
          :disabled="disabled || !hasDrawn"
          title="ย้อนกลับ (Undo)"
          class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/80 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <RotateCcw class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">ย้อนกลับ</span>
        </button>

        <button
          type="button"
          @click="redo"
          :disabled="disabled || redoStack.length === 0"
          title="ทำซ้ำ (Redo)"
          class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/80 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <RotateCw class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">ทำซ้ำ</span>
        </button>

        <button
          type="button"
          @click="clear"
          :disabled="disabled"
          title="ล้างหน้าจอ (Clear)"
          class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-rose-200 dark:border-rose-950 bg-rose-50/50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 hover:bg-rose-100/70 dark:hover:bg-rose-950/40 transition-colors disabled:opacity-40 disabled:cursor-not-allowed font-medium"
        >
          <Trash2 class="w-3.5 h-3.5" />
          <span>ล้างหน้าจอ</span>
        </button>
      </div>
    </div>
  </div>
</template>
