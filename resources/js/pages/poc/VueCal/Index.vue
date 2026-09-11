<script setup lang="ts">
import { computed, ref } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import VueCal from 'vue-cal';
import 'vue-cal/dist/vuecal.css';
import 'vue-cal/dist/drag-and-drop.es.js';

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'vue-sonner';
import {
    ArrowLeft,
    Building2,
    CalendarDays,
    Columns3,
    CreditCard,
    Filter,
    Move,
    Plus,
    Sparkles,
} from '@lucide/vue';

import type { Appointment } from '../mockData';
import { clinicBranches, getInitialAppointments } from '../mockData';
import BillingDialog from '../BillingDialog.vue';
import AppointmentFormDialog from '../AppointmentFormDialog.vue';

// 1. Reactive State
const appointments = ref<Appointment[]>(getInitialAppointments());
const selectedBranchId = ref<string>('all'); // 'all' | 'b1' | 'b2' | 'b3'
const isSplitViewMode = ref<boolean>(true); // Split days toggle

// Dialogs state
const isBillingOpen = ref(false);
const selectedBillingAppointment = ref<Appointment | null>(null);

const isFormOpen = ref(false);
const editingAppointment = ref<Appointment | null>(null);
const formInitialDate = ref<string>('');

// Format helper: Convert ISO "2026-09-11T09:00:00" to "2026-09-11 09:00" for Vue-Cal
function toVueCalDate(isoStr: string): string {
    return isoStr.replace('T', ' ').slice(0, 16);
}

// 2. Vue-Cal Split Days Configuration (3 Branches Side-by-Side)
const splitDays = [
    { id: 1, branchKey: 'b1', label: '🏢 สาขา สยามสแควร์', class: 'split-siam' },
    { id: 2, branchKey: 'b2', label: '🏢 สาขา อารีย์', class: 'split-ari' },
    { id: 3, branchKey: 'b3', label: '🏢 สาขา ทองหล่อ', class: 'split-thonglo' },
];

function getSplitNumber(branchId: string): number {
    if (branchId === 'b1') return 1;
    if (branchId === 'b2') return 2;
    return 3;
}

// 3. Branch Filter
const filteredAppointments = computed(() => {
    if (selectedBranchId.value === 'all') {
        return appointments.value;
    }
    return appointments.value.filter((apt) => apt.branchId === selectedBranchId.value);
});

// Map appointments to Vue-Cal Event format
const vueCalEvents = computed(() => {
    return filteredAppointments.value.map((apt) => {
        const branch = clinicBranches.find((b) => b.id === apt.branchId);
        return {
            id: apt.id,
            title: apt.title,
            start: toVueCalDate(apt.start),
            end: toVueCalDate(apt.end),
            split: getSplitNumber(apt.branchId),
            class: apt.status === 'paid' ? 'event-paid' : `event-${apt.branchId}`,
            // Custom extended props
            patientName: apt.patientName,
            patientPhone: apt.patientPhone,
            doctorName: apt.doctorName,
            branchName: branch?.name.split(' (')[0] || '',
            branchId: apt.branchId,
            treatment: apt.treatment,
            price: apt.price,
            status: apt.status,
        };
    });
});

// 4. Drag & Drop and Event Change Handlers
function onEventChange(eventData: any) {
    const apt = appointments.value.find((a) => a.id === eventData.id || a.id === eventData.event?.id);
    const targetEvent = eventData.event || eventData;
    if (apt && targetEvent) {
        // Update times
        if (targetEvent.start) {
            const startStr = typeof targetEvent.start === 'string' ? targetEvent.start : targetEvent.start.format('YYYY-MM-DD HH:mm');
            apt.start = `${startStr.replace(' ', 'T')}:00`;
        }
        if (targetEvent.end) {
            const endStr = typeof targetEvent.end === 'string' ? targetEvent.end : targetEvent.end.format('YYYY-MM-DD HH:mm');
            apt.end = `${endStr.replace(' ', 'T')}:00`;
        }

        // Check if dragged to another split column
        if (targetEvent.split) {
            const newBranchKey = splitDays.find((s) => s.id === targetEvent.split)?.branchKey;
            if (newBranchKey && (newBranchKey === 'b1' || newBranchKey === 'b2' || newBranchKey === 'b3')) {
                apt.branchId = newBranchKey;
            }
        }

        toast.success('อัปเดตเวลานัดหมายสำเร็จ (Vue-Cal Drag & Drop)', {
            description: `${apt.patientName}: เวลาใหม่ ${apt.start.slice(11, 16)} น.`
        });
    }
}

// 5. Actions
function handleOpenBilling(event: any) {
    const apt = appointments.value.find((a) => a.id === event.id);
    if (apt) {
        selectedBillingAppointment.value = apt;
        isBillingOpen.value = true;
    }
}

function handleCellClick(date: Date) {
    formInitialDate.value = date.toISOString().split('T')[0];
    editingAppointment.value = null;
    isFormOpen.value = true;
}

function handleEditAppointment(event: any) {
    const apt = appointments.value.find((a) => a.id === event.id);
    if (apt) {
        editingAppointment.value = apt;
        isFormOpen.value = true;
    }
}

function handleSaveAppointment(newApt: Appointment) {
    const index = appointments.value.findIndex((a) => a.id === newApt.id);
    if (index >= 0) {
        appointments.value[index] = newApt;
    } else {
        appointments.value.push(newApt);
    }
}

function handleMarkAsPaid(appointmentId: string) {
    const apt = appointments.value.find((a) => a.id === appointmentId);
    if (apt) {
        apt.status = 'paid';
    }
}
</script>

<template>
    <Head title="PoC Vue-Cal - Clinic Appointment" />

    <div class="flex-1 space-y-5 p-4 md:p-6 max-w-[1600px] mx-auto">
        <!-- Header Banner & Comparison Switcher -->
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b pb-4">
            <div>
                <div class="flex items-center gap-2.5">
                    <span class="rounded-lg bg-emerald-500/10 p-2 text-emerald-600 dark:text-emerald-400">
                        <CalendarDays class="size-6" />
                    </span>
                    <div>
                        <div class="flex items-center gap-2">
                            <h1 class="text-2xl font-bold tracking-tight">
                                PoC 2: Vue-Cal (v4/v5)
                            </h1>
                            <Badge variant="secondary" class="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300">
                                🥈 จุดเด่น: แยกคอลัมน์หลายสาขาฟรี
                            </Badge>
                        </div>
                        <p class="text-xs md:text-sm text-muted-foreground mt-0.5">
                            ทดสอบฟังก์ชัน Split Days แสดง 3 เสาสาขาคู่ขนานในวันเดียวกัน พร้อม Drag & Drop ข้ามสาขา
                        </p>
                    </div>
                </div>
            </div>

            <!-- Switcher to FullCalendar -->
            <Link href="/poc/fullcalendar">
                <Button variant="outline" class="gap-2 border-emerald-600/40 hover:bg-emerald-500/5">
                    <ArrowLeft class="size-4 text-emerald-600" />
                    <span>กลับไปดู PoC 1: FullCalendar</span>
                </Button>
            </Link>
        </div>

        <!-- Filter & View Controls -->
        <Card class="shadow-xs border bg-card">
            <CardContent class="p-3.5 flex flex-wrap items-center justify-between gap-3">
                <div class="flex flex-wrap items-center gap-3">
                    <!-- Branch Filter Dropdown -->
                    <div class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                        <Filter class="size-4 text-emerald-600" />
                        <span>กรองสาขา:</span>
                    </div>

                    <Select v-model="selectedBranchId">
                        <SelectTrigger class="w-[220px] font-medium">
                            <SelectValue placeholder="เลือกสาขา" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">
                                🏢 ทั้งหมด (ทุกสาขา)
                            </SelectItem>
                            <SelectItem
                                v-for="b in clinicBranches"
                                :key="b.id"
                                :value="b.id"
                            >
                                {{ b.name.split(' (')[0] }}
                            </SelectItem>
                        </SelectContent>
                    </Select>

                    <!-- Toggle Split Days Mode -->
                    <Button
                        variant="outline"
                        size="sm"
                        @click="isSplitViewMode = !isSplitViewMode"
                        class="gap-1.5 text-xs font-semibold"
                        :class="isSplitViewMode ? 'border-emerald-500 bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : ''"
                    >
                        <Columns3 class="size-4" />
                        {{ isSplitViewMode ? 'เปิดมุมมองแยก 3 เสาสาขา (Split Mode)' : 'มุมมองวันปกติ (Single Column)' }}
                    </Button>
                </div>

                <div class="flex items-center gap-2">
                    <Button
                        size="sm"
                        class="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold gap-1.5 shadow-xs"
                        @click="() => { editingAppointment = null; formInitialDate = ''; isFormOpen = true; }"
                    >
                        <Plus class="size-4" />
                        เพิ่มนัดหมายใหม่
                    </Button>
                </div>
            </CardContent>
        </Card>

        <!-- Vue-Cal Calendar Container -->
        <Card class="shadow-sm border overflow-hidden">
            <CardContent class="p-3 md:p-5 vuecal-clinic-wrapper">
                <vue-cal
                    class="vuecal--clinic-theme"
                    active-view="week"
                    :disable-views="['years', 'year']"
                    :time-from="8 * 60"
                    :time-to="20 * 60"
                    :time-step="30"
                    :time-cell-height="60"
                    :events="vueCalEvents"
                    :split-days="isSplitViewMode && selectedBranchId === 'all' ? splitDays : []"
                    :sticky-split-labels="true"
                    :editable-events="{ title: false, drag: true, resize: true, delete: false, create: false }"
                    :drag-to-create-event="false"
                    @event-change="onEventChange"
                    @event-drop="onEventChange"
                    @cell-click="handleCellClick"
                >
                    <!-- 🎯 Split Header Label -->
                    <template #split-label="{ split }">
                        <div class="font-bold text-xs py-1 text-center">
                            {{ split.label }}
                        </div>
                    </template>

                    <!-- 🎯 Custom Event Slot: แสดงชื่อคนไข้ + ปุ่มออกบิล -->
                    <template #event="{ event }">
                        <div
                            class="flex flex-col justify-between w-full h-full p-1.5 rounded text-left overflow-hidden select-none cursor-pointer"
                            @click="handleEditAppointment(event)"
                        >
                            <!-- Top: Patient Name & Treatment -->
                            <div class="space-y-0.5">
                                <div class="font-bold text-xs truncate leading-tight flex items-center justify-between">
                                    <span>👤 {{ event.patientName }}</span>
                                    <span v-if="event.status === 'paid'" class="text-[9px] bg-emerald-800 text-white px-1 rounded">
                                        จ่ายแล้ว
                                    </span>
                                </div>
                                <div class="text-[11px] opacity-90 truncate font-medium">
                                    {{ event.title }}
                                </div>
                                <div class="text-[10px] opacity-75 truncate">
                                    👨‍⚕️ {{ event.doctorName?.split(' ')[1] }}
                                </div>
                            </div>

                            <!-- Bottom: Branch Name & Action Button (ออกบิล) -->
                            <div class="flex items-center justify-between gap-1 mt-1 pt-1 border-t border-current/20">
                                <span class="text-[9px] px-1 py-0.2 rounded bg-black/15 font-mono truncate max-w-[65px]">
                                    {{ event.branchName }}
                                </span>

                                <!-- 💳 ปุ่มออกบิล (stop propagation) -->
                                <button
                                    type="button"
                                    @click.stop="handleOpenBilling(event)"
                                    class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold shadow-xs transition-transform active:scale-95 bg-amber-400 text-amber-950 hover:bg-amber-300"
                                    title="คลิกเพื่อออกบิลค่ารักษา"
                                >
                                    <CreditCard class="size-3" />
                                    <span>{{ event.status === 'paid' ? 'ดูบิล' : 'ออกบิล' }}</span>
                                </button>
                            </div>
                        </div>
                    </template>
                </vue-cal>
            </CardContent>
        </Card>

        <!-- Feature Guide Footer -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
            <div class="p-3 rounded-lg border bg-card/60 flex items-start gap-2.5">
                <Columns3 class="size-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold">1. เสาสาขาคู่ขนาน (Split Days):</span>
                    <p class="text-muted-foreground mt-0.5">ดู 3 สาขาพร้อมกันในหน้าเดียว และลากข้ามเสาสาขาเพื่อย้ายสาขาได้</p>
                </div>
            </div>
            <div class="p-3 rounded-lg border bg-card/60 flex items-start gap-2.5">
                <Filter class="size-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold">2. กรองทีละสาขา:</span>
                    <p class="text-muted-foreground mt-0.5">เลือกสาขาเดียวจาก Dropdown เพื่อยุบรวมดูเฉพาะสาขานั้น</p>
                </div>
            </div>
            <div class="p-3 rounded-lg border bg-card/60 flex items-start gap-2.5">
                <Move class="size-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold">3. ลากวาง (Drag & Drop):</span>
                    <p class="text-muted-foreground mt-0.5">ลากเพื่อเปลี่ยนเวลา และยืดหดเวลาการรักษาได้ในตัว</p>
                </div>
            </div>
            <div class="p-3 rounded-lg border bg-card/60 flex items-start gap-2.5">
                <CreditCard class="size-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold">4. ปุ่มออกบิลในกล่อง:</span>
                    <p class="text-muted-foreground mt-0.5">คลิกปุ่ม "ออกบิล" เพื่อเปิด Mock Billing และบันทึกสถานะ</p>
                </div>
            </div>
        </div>

        <!-- Modals -->
        <BillingDialog
            v-model:open="isBillingOpen"
            :appointment="selectedBillingAppointment"
            @paid="handleMarkAsPaid"
        />

        <AppointmentFormDialog
            v-model:open="isFormOpen"
            :initial-date="formInitialDate"
            :initial-branch-id="selectedBranchId === 'all' ? 'b1' : (selectedBranchId as 'b1' | 'b2' | 'b3')"
            :editing-appointment="editingAppointment"
            @save="handleSaveAppointment"
        />
    </div>
</template>

<style>
/* Vue-Cal Theme Overrides for Clean Clinic UI */
.vuecal-clinic-wrapper .vuecal {
    height: 750px;
    background-color: var(--card, #ffffff);
    color: var(--foreground, #0f172a);
    border-radius: 0.5rem;
    border: 1px solid var(--border, #e2e8f0);
}

.vuecal-clinic-wrapper .vuecal__menu,
.vuecal-clinic-wrapper .vuecal__view-selector {
    background-color: var(--muted, #f8fafc);
}

.vuecal-clinic-wrapper .vuecal__view-btn {
    border-radius: 0.375rem;
    font-size: 0.8rem;
    font-weight: 500;
}

.vuecal-clinic-wrapper .vuecal__view-btn--active {
    background-color: #059669 !important;
    color: #ffffff !important;
}

.vuecal-clinic-wrapper .vuecal__title-bar {
    background-color: var(--muted, #f8fafc);
}

.vuecal-clinic-wrapper .vuecal__event {
    border-radius: 0.375rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    color: #ffffff;
}

.vuecal-clinic-wrapper .event-b1 {
    background-color: #2563eb !important;
    border: 1px solid #1d4ed8;
}

.vuecal-clinic-wrapper .event-b2 {
    background-color: #059669 !important;
    border: 1px solid #047857;
}

.vuecal-clinic-wrapper .event-b3 {
    background-color: #7c3aed !important;
    border: 1px solid #6d28d9;
}

.vuecal-clinic-wrapper .event-paid {
    background-color: #10b981 !important;
    border: 1px solid #059669;
}

.vuecal-clinic-wrapper .split-siam {
    background-color: rgba(37, 99, 235, 0.03);
}

.vuecal-clinic-wrapper .split-ari {
    background-color: rgba(5, 150, 105, 0.03);
}

.vuecal-clinic-wrapper .split-thonglo {
    background-color: rgba(124, 58, 237, 0.03);
}
</style>
