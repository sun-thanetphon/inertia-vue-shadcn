<script setup lang="ts">
import { computed, ref } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { toast } from 'vue-sonner';
import {
    ArrowRight,
    Building2,
    Calendar as CalendarIcon,
    CheckCircle2,
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
const calendarRef = ref<any>(null);

// Dialogs state
const isBillingOpen = ref(false);
const selectedBillingAppointment = ref<Appointment | null>(null);

const isFormOpen = ref(false);
const editingAppointment = ref<Appointment | null>(null);
const formInitialDate = ref<string>('');

// 2. Branch Filtering
const filteredAppointments = computed(() => {
    if (selectedBranchId.value === 'all') {
        return appointments.value;
    }
    return appointments.value.filter((apt) => apt.branchId === selectedBranchId.value);
});

// Map to FullCalendar Event Format
const calendarEvents = computed(() => {
    return filteredAppointments.value.map((apt) => {
        const branch = clinicBranches.find((b) => b.id === apt.branchId);
        return {
            id: apt.id,
            title: apt.title,
            start: apt.start,
            end: apt.end,
            backgroundColor: apt.status === 'paid' ? '#10b981' : branch?.color || '#3b82f6',
            borderColor: apt.status === 'paid' ? '#059669' : branch?.color || '#3b82f6',
            extendedProps: {
                ...apt,
                branchName: branch?.name.split(' (')[0] || '',
            },
        };
    });
});

// 3. FullCalendar Configuration
const calendarOptions = computed(() => ({
    plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
    initialView: 'timeGridWeek',
    headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay',
    },
    buttonText: {
        today: 'วันนี้',
        month: 'เดือน',
        week: 'สัปดาห์',
        day: 'วัน',
    },
    slotMinTime: '08:00:00',
    slotMaxTime: '20:00:00',
    allDaySlot: false,
    height: 'auto',
    expandRows: true,
    nowIndicator: true,
    editable: true, // Enable Drag & Drop + Resize
    selectable: true,
    selectMirror: true,
    dayMaxEvents: true,
    events: calendarEvents.value,

    // Drag & Drop Handler (ลากวางเลื่อนเวลานัดหมาย)
    eventDrop: (info: any) => {
        const apt = appointments.value.find((a) => a.id === info.event.id);
        if (apt) {
            apt.start = info.event.start.toISOString().slice(0, 19);
            apt.end = info.event.end
                ? info.event.end.toISOString().slice(0, 19)
                : new Date(info.event.start.getTime() + 60 * 60 * 1000).toISOString().slice(0, 19);

            const timeStr = info.event.start.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
            const dateStr = info.event.start.toLocaleDateString('th-TH', { dateStyle: 'medium' });

            toast.success('ย้ายเวลานัดหมายสำเร็จ (Drag & Drop)', {
                description: `${apt.patientName}: ย้ายไปวันที่ ${dateStr} เวลา ${timeStr} น.`
            });
        }
    },

    // Resize Duration Handler
    eventResize: (info: any) => {
        const apt = appointments.value.find((a) => a.id === info.event.id);
        if (apt && info.event.end) {
            apt.end = info.event.end.toISOString().slice(0, 19);
            const endTimeStr = info.event.end.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
            toast.info('ปรับระยะเวลาตรวจสำเร็จ', {
                description: `${apt.patientName}: เวลาสิ้นสุดใหม่คือ ${endTimeStr} น.`
            });
        }
    },

    // Click on calendar empty slot to add appointment
    select: (selectionInfo: any) => {
        formInitialDate.value = selectionInfo.startStr.split('T')[0];
        editingAppointment.value = null;
        isFormOpen.value = true;
    },

    // Click on event card to edit
    eventClick: (clickInfo: any) => {
        const apt = appointments.value.find((a) => a.id === clickInfo.event.id);
        if (apt) {
            editingAppointment.value = apt;
            isFormOpen.value = true;
        }
    },
}));

// 4. Action Handlers
function handleOpenBilling(aptData: any) {
    const apt = appointments.value.find((a) => a.id === aptData.id);
    if (apt) {
        selectedBillingAppointment.value = apt;
        isBillingOpen.value = true;
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
    <Head title="PoC FullCalendar Vue 3 - Clinic Appointment" />

    <div class="flex-1 space-y-5 p-4 md:p-6 max-w-[1600px] mx-auto">
        <!-- Header Banner & Comparison Switcher -->
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b pb-4">
            <div>
                <div class="flex items-center gap-2.5">
                    <span class="rounded-lg bg-primary/10 p-2 text-primary">
                        <CalendarIcon class="size-6" />
                    </span>
                    <div>
                        <div class="flex items-center gap-2">
                            <h1 class="text-2xl font-bold tracking-tight">
                                PoC 1: FullCalendar Vue 3
                            </h1>
                            <Badge variant="secondary" class="bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300">
                                🥇 อันดับ 1 แนะนำ
                            </Badge>
                        </div>
                        <p class="text-xs md:text-sm text-muted-foreground mt-0.5">
                            ทดสอบการจัดตารางนัดหมายคลินิก: กรองสาขา, ลากวาง (Drag & Drop), คลิกออกบิล และเพิ่มนัดหมาย
                        </p>
                    </div>
                </div>
            </div>

            <!-- Switcher to Vue-Cal -->
            <Link href="/poc/vue-cal">
                <Button variant="outline" class="gap-2 border-primary/40 hover:bg-primary/5">
                    <span>เปรียบเทียบกับ PoC 2: Vue-Cal</span>
                    <ArrowRight class="size-4 text-primary" />
                </Button>
            </Link>
        </div>

        <!-- Filter & Control Bar -->
        <Card class="shadow-xs border bg-card">
            <CardContent class="p-3.5 flex flex-wrap items-center justify-between gap-3">
                <div class="flex items-center gap-3">
                    <div class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                        <Filter class="size-4 text-primary" />
                        <span>กรองสาขาคลินิก:</span>
                    </div>

                    <!-- Branch Selector -->
                    <Select v-model="selectedBranchId">
                        <SelectTrigger class="w-[240px] font-medium">
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
                                <div class="flex items-center gap-2">
                                    <span class="size-2 rounded-full" :style="{ backgroundColor: b.color }" />
                                    <span>{{ b.name.split(' (')[0] }}</span>
                                </div>
                            </SelectItem>
                        </SelectContent>
                    </Select>

                    <!-- Active Branch Indicator -->
                    <div class="hidden sm:flex items-center gap-1.5 text-xs text-muted-foreground">
                        <span>แสดงอยู่:</span>
                        <Badge variant="outline" class="font-semibold text-xs">
                            {{ filteredAppointments.length }} นัดหมาย
                        </Badge>
                    </div>
                </div>

                <div class="flex items-center gap-2">
                    <Button
                        size="sm"
                        class="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold gap-1.5 shadow-xs"
                        @click="() => { editingAppointment = null; formInitialDate = ''; isFormOpen = true; }"
                    >
                        <Plus class="size-4" />
                        เพิ่มนัดหมายใหม่
                    </Button>
                </div>
            </CardContent>
        </Card>

        <!-- Calendar Container -->
        <Card class="shadow-sm border overflow-hidden">
            <CardContent class="p-3 md:p-5 fullcalendar-clinic-wrapper">
                <FullCalendar ref="calendarRef" :options="calendarOptions">
                    <!-- 🎯 Custom Event Content Slot -->
                    <template #eventContent="{ event }">
                        <div
                            class="flex flex-col justify-between w-full h-full p-1.5 rounded text-left overflow-hidden select-none"
                            :class="[
                                event.extendedProps.status === 'paid'
                                    ? 'bg-emerald-600 text-white'
                                    : 'bg-primary/95 text-primary-foreground'
                            ]"
                        >
                            <!-- Top: Patient Name & Treatment -->
                            <div class="space-y-0.5">
                                <div class="font-bold text-xs truncate leading-tight flex items-center justify-between">
                                    <span>👤 {{ event.extendedProps.patientName }}</span>
                                    <span v-if="event.extendedProps.status === 'paid'" class="text-[10px] font-normal bg-black/20 px-1 rounded">
                                        ชำระแล้ว
                                    </span>
                                </div>
                                <div class="text-[11px] opacity-90 truncate font-medium">
                                    {{ event.title }}
                                </div>
                                <div class="text-[10px] opacity-75 truncate">
                                    👨‍⚕️ {{ event.extendedProps.doctorName?.split(' ')[1] }}
                                </div>
                            </div>

                            <!-- Bottom: Branch Badge & Action Button (ออกบิล) -->
                            <div class="flex items-center justify-between gap-1 mt-1 pt-1 border-t border-white/20">
                                <span class="text-[9px] px-1 py-0.2 rounded bg-black/25 font-mono truncate max-w-[70px]">
                                    {{ event.extendedProps.branchName }}
                                </span>

                                <!-- 💳 ปุ่มออกบิล (stop propagation เพื่อไม่ให้ trigger click event) -->
                                <button
                                    type="button"
                                    @click.stop="handleOpenBilling(event.extendedProps)"
                                    class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold shadow-xs transition-transform active:scale-95"
                                    :class="[
                                        event.extendedProps.status === 'paid'
                                            ? 'bg-white text-emerald-800 hover:bg-slate-100'
                                            : 'bg-amber-400 text-amber-950 hover:bg-amber-300'
                                    ]"
                                    title="คลิกเพื่อออกบิลค่ารักษา"
                                >
                                    <CreditCard class="size-3" />
                                    <span>{{ event.extendedProps.status === 'paid' ? 'ดูบิล' : 'ออกบิล' }}</span>
                                </button>
                            </div>
                        </div>
                    </template>
                </FullCalendar>
            </CardContent>
        </Card>

        <!-- Feature Guide Footer -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
            <div class="p-3 rounded-lg border bg-card/60 flex items-start gap-2.5">
                <Plus class="size-4 text-primary shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold">1. เพิ่มนัดหมาย:</span>
                    <p class="text-muted-foreground mt-0.5">กดปุ่ม "+ เพิ่มนัดหมายใหม่" หรือคลิกที่ช่องว่างบนปฏิทิน</p>
                </div>
            </div>
            <div class="p-3 rounded-lg border bg-card/60 flex items-start gap-2.5">
                <Filter class="size-4 text-primary shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold">2. กรองสาขา:</span>
                    <p class="text-muted-foreground mt-0.5">เลือกสาขาจาก Dropdown ด้านบน นัดหมายจะกรองเฉพาะสาขานั้นทันที</p>
                </div>
            </div>
            <div class="p-3 rounded-lg border bg-card/60 flex items-start gap-2.5">
                <Move class="size-4 text-primary shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold">3. ลากวาง (Drag & Drop):</span>
                    <p class="text-muted-foreground mt-0.5">ลากกล่องนัดหมายเพื่อเลื่อนวันและเวลาตรวจได้ทันที</p>
                </div>
            </div>
            <div class="p-3 rounded-lg border bg-card/60 flex items-start gap-2.5">
                <CreditCard class="size-4 text-primary shrink-0 mt-0.5" />
                <div>
                    <span class="font-bold">4. ปุ่มออกบิลในกล่อง:</span>
                    <p class="text-muted-foreground mt-0.5">คลิกปุ่ม "ออกบิล" ข้างใน Event เพื่อเปิดหน้าจอ Mock Billing</p>
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
/* FullCalendar Custom CSS Variables for Seamless Tailwind/Shadcn Theme */
.fullcalendar-clinic-wrapper .fc {
    --fc-border-color: var(--border, #e2e8f0);
    --fc-today-bg-color: rgba(59, 130, 246, 0.05);
    --fc-now-indicator-color: #ef4444;
    font-family: inherit;
}

.fullcalendar-clinic-wrapper .fc-theme-standard td,
.fullcalendar-clinic-wrapper .fc-theme-standard th {
    border-color: var(--border, #e2e8f0);
}

.fullcalendar-clinic-wrapper .fc-toolbar-title {
    font-size: 1.15rem !important;
    font-weight: 700;
}

.fullcalendar-clinic-wrapper .fc-button-primary {
    background-color: var(--card, #ffffff) !important;
    color: var(--foreground, #0f172a) !important;
    border: 1px solid var(--border, #cbd5e1) !important;
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.75rem !important;
    border-radius: 0.5rem !important;
    text-transform: capitalize !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
}

.fullcalendar-clinic-wrapper .fc-button-primary:hover {
    background-color: var(--muted, #f1f5f9) !important;
}

.fullcalendar-clinic-wrapper .fc-button-primary.fc-button-active {
    background-color: var(--primary, #0f172a) !important;
    color: var(--primary-foreground, #ffffff) !important;
    border-color: var(--primary, #0f172a) !important;
}

.fullcalendar-clinic-wrapper .fc-timegrid-event-harness {
    margin: 1px 2px !important;
}

.fullcalendar-clinic-wrapper .fc-event {
    border-radius: 0.375rem !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
    border: none !important;
    overflow: hidden !important;
}
</style>
