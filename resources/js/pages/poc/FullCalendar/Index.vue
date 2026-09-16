<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { Head, Link } from '@inertiajs/vue3';
import { useBreakpoints, breakpointsTailwind } from '@vueuse/core';
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
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'vue-sonner';
import {
    Calendar as CalendarIcon,
    Clock,
    CreditCard,
    Edit3,
    Filter,
    Move,
    Phone,
    Plus,
} from '@lucide/vue';

import type { Appointment } from '../mockData';
import { clinicBranches, getInitialAppointments } from '../mockData';
import BillingDialog from '../BillingDialog.vue';
import AppointmentFormDialog from '../AppointmentFormDialog.vue';

// 1. Reactive State
const appointments = ref<Appointment[]>(getInitialAppointments());
const selectedBranchId = ref<string>('all'); // 'all' | 'b1' | 'b2' | 'b3'
const calendarRef = ref<any>(null);

// Responsive Breakpoints: Auto adapt view to mobile (< 768px)
const breakpoints = useBreakpoints(breakpointsTailwind);
const isMobile = breakpoints.smaller('md');

// Watch isMobile to adapt FullCalendar view reactively
watch(
    isMobile,
    (val) => {
        const api = calendarRef.value?.getApi();
        if (api) {
            api.changeView(val ? 'timeGridDay' : 'timeGridWeek');
        }
    },
);

// Dialogs state
const isBillingOpen = ref(false);
const selectedBillingAppointment = ref<Appointment | null>(null);

const isFormOpen = ref(false);
const editingAppointment = ref<Appointment | null>(null);
const formInitialDate = ref<string>('');

// Format & Initials helpers
function getInitials(name: string): string {
    if (!name) return 'คน';
    const clean = name.replace(/^(นาย|นางสาว|นาง|คุณ|ทพ\.|ทพญ\.|ดร\.)\s*/, '').trim();
    return clean.slice(0, 2) || name.slice(0, 2);
}

// Format helper
function formatTime(val: any): string {
    if (!val) return '';
    if (typeof val === 'string') {
        if (val.includes(' ') || val.includes('T')) {
            const timePart = val.includes('T')
                ? val.split('T')[1]
                : val.split(' ')[1];
            return timePart.slice(0, 5);
        }
        return val.slice(0, 5);
    }
    if (val instanceof Date) {
        const hours = String(val.getHours()).padStart(2, '0');
        const mins = String(val.getMinutes()).padStart(2, '0');
        return `${hours}:${mins}`;
    }
    return '';
}

// 2. Branch Filtering
const filteredAppointments = computed(() => {
    if (selectedBranchId.value === 'all') {
        return appointments.value;
    }
    return appointments.value.filter(
        (apt) => apt.branchId === selectedBranchId.value,
    );
});

// Quick Branch Filter Pills
const branchPills = computed(() => [
    {
        id: 'all',
        name: '🏢 ทุกสาขา',
        count: appointments.value.length,
        color: '',
    },
    ...clinicBranches.map((b) => ({
        id: b.id,
        name: b.name.split(' (')[0],
        count: appointments.value.filter((a) => a.branchId === b.id).length,
        color: b.color,
    })),
]);

// Map to FullCalendar Event Format
const calendarEvents = computed(() => {
    return filteredAppointments.value.map((apt) => {
        const branch = clinicBranches.find((b) => b.id === apt.branchId);
        return {
            id: apt.id,
            title: apt.title,
            start: apt.start,
            end: apt.end,
            backgroundColor: 'transparent',
            borderColor: 'transparent',
            extendedProps: {
                ...apt,
                branchName: branch?.name.split(' (')[0] || '',
                branchColor: branch?.color || '#3b82f6',
            },
        };
    });
});

// 3. FullCalendar Configuration
const calendarOptions = computed(() => ({
    plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
    initialView: isMobile.value ? 'timeGridDay' : 'timeGridWeek',
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
    slotDuration: '00:30:00',
    allDaySlot: false,
    height: 'auto',
    expandRows: true,
    eventMinHeight: 60,
    eventShortHeight: 50,
    nowIndicator: true,
    scrollTime: '08:30:00',
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
                : new Date(info.event.start.getTime() + 60 * 60 * 1000)
                      .toISOString()
                      .slice(0, 19);

            const timeStr = info.event.start.toLocaleTimeString('th-TH', {
                hour: '2-digit',
                minute: '2-digit',
            });
            const dateStr = info.event.start.toLocaleDateString('th-TH', {
                dateStyle: 'medium',
            });

            toast.success('ย้ายเวลานัดหมายสำเร็จ (Drag & Drop)', {
                description: `${apt.patientName}: ย้ายไปวันที่ ${dateStr} เวลา ${timeStr} น.`,
            });
        }
    },

    // Resize Duration Handler
    eventResize: (info: any) => {
        const apt = appointments.value.find((a) => a.id === info.event.id);
        if (apt && info.event.end) {
            apt.end = info.event.end.toISOString().slice(0, 19);
            const endTimeStr = info.event.end.toLocaleTimeString('th-TH', {
                hour: '2-digit',
                minute: '2-digit',
            });
            toast.info('ปรับระยะเวลาตรวจสำเร็จ', {
                description: `${apt.patientName}: เวลาสิ้นสุดใหม่คือ ${endTimeStr} น.`,
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

function handleEditAppointment(aptData: any) {
    const apt = appointments.value.find((a) => a.id === aptData.id);
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
    <Head title="PoC FullCalendar Vue 3 - Clinic Appointment" />

    <div
        class="mx-auto flex min-h-screen w-full max-w-[1750px] min-w-0 flex-1 flex-col justify-start space-y-4 p-3 sm:p-4 md:p-6"
    >
        <!-- Header Banner & Comparison Switcher (Responsive) -->
        <header
            class="flex flex-col gap-3 border-b pb-4 sm:flex-row sm:items-center sm:justify-between"
        >
            <div class="flex items-center gap-2.5">
                <span class="bg-primary/10 text-primary rounded-lg p-2">
                    <CalendarIcon class="size-5 sm:size-6" />
                </span>
                <div>
                    <div class="flex flex-wrap items-center gap-2">
                        <h1
                            class="text-foreground text-xl font-bold tracking-tight sm:text-2xl"
                        >
                            PoC 1: FullCalendar Vue 3
                        </h1>
                        <Badge
                            variant="secondary"
                            class="bg-blue-100 text-xs text-blue-800 dark:bg-blue-900/50 dark:text-blue-300"
                        >
                            Shadcn CSS Theme
                        </Badge>
                    </div>
                    <p
                        class="text-muted-foreground line-clamp-1 text-xs sm:text-sm"
                    >
                        ทดสอบการจัดตารางนัดหมายคลินิก: กรองสาขา, ลากวาง (Drag & Drop), ออกบิล และเพิ่มนัดหมาย
                    </p>
                </div>
            </div>
        </header>

        <!-- Filter & Control Bar (Responsive) -->
        <Card class="bg-card border shadow-xs">
            <CardContent
                class="flex flex-col gap-3 p-3 sm:flex-row sm:items-center sm:justify-between sm:p-3.5"
            >
                <!-- Quick Branch Pills for 1-Tap Switching -->
                <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
                    <div
                        class="text-muted-foreground mr-1 flex items-center gap-1.5 text-xs font-medium"
                    >
                        <Filter class="text-primary size-3.5" />
                        <span>สาขา:</span>
                    </div>

                    <Button
                        v-for="pill in branchPills"
                        :key="pill.id"
                        size="sm"
                        :variant="selectedBranchId === pill.id ? 'default' : 'outline'"
                        class="h-7 text-xs font-medium gap-1.5 transition-all shadow-2xs cursor-pointer"
                        @click="selectedBranchId = pill.id"
                    >
                        <span
                            v-if="pill.color"
                            class="size-2 rounded-full shrink-0"
                            :style="{ backgroundColor: pill.color }"
                        />
                        <span>{{ pill.name }}</span>
                        <Badge
                            variant="secondary"
                            class="ml-0.5 h-4 px-1 text-[10px] font-mono"
                            :class="
                                selectedBranchId === pill.id
                                    ? 'bg-primary-foreground/20 text-primary-foreground'
                                    : 'bg-muted text-muted-foreground'
                            "
                        >
                            {{ pill.count }}
                        </Badge>
                    </Button>
                </div>

                <div class="flex items-center gap-2">
                    <Button
                        size="sm"
                        class="h-8 w-full gap-1.5 text-xs font-semibold shadow-xs sm:w-auto"
                        @click="
                            () => {
                                editingAppointment = null;
                                formInitialDate = '';
                                isFormOpen = true;
                            }
                        "
                    >
                        <Plus class="size-3.5" />
                        <span>เพิ่มนัดหมายใหม่</span>
                    </Button>
                </div>
            </CardContent>
        </Card>

        <!-- Calendar Container (Shadcn Card Shell) -->
        <Card class="border shadow-xs overflow-hidden">
            <CardContent class="p-2 sm:p-4 md:p-5 fullcalendar-clinic-wrapper">
                <FullCalendar ref="calendarRef" :options="calendarOptions">
                    <!-- 🎯 Custom Event Content Slot: Pure Shadcn UI Card Aesthetic -->
                    <template #eventContent="{ event, view }">
                        <!-- 1. Month View: Sleek Shadcn Event Pill -->
                        <div
                            v-if="view.type === 'dayGridMonth'"
                            class="clinic-month-pill group flex w-full items-center gap-1.5 overflow-hidden rounded border border-border/80 bg-card px-1.5 py-0.5 text-left text-[11px] leading-tight text-card-foreground shadow-2xs transition-all hover:border-primary/40 hover:bg-muted/70 cursor-pointer select-none"
                            :style="{
                                borderLeftWidth: '3px',
                                borderLeftColor:
                                    event.extendedProps.status === 'paid'
                                        ? '#10b981'
                                        : event.extendedProps.branchColor,
                            }"
                            :title="`${event.extendedProps.patientName} - ${event.title} (${formatTime(event.start)})`"
                            @click="handleEditAppointment(event.extendedProps)"
                        >
                            <span
                                class="size-1.5 shrink-0 rounded-full"
                                :class="
                                    event.extendedProps.status === 'paid'
                                        ? 'bg-emerald-500'
                                        : 'bg-amber-500 animate-pulse'
                                "
                            />
                            <span class="shrink-0 font-mono text-[9px] text-muted-foreground">
                                {{ formatTime(event.start) }}
                            </span>
                            <span class="truncate font-medium text-foreground text-[10px] sm:text-[11px]">
                                {{ event.extendedProps.patientName }}
                            </span>
                        </div>

                        <!-- 2. TimeGrid View (Week & Day): Adaptive Container-Aware Clinic Card -->
                        <article
                            v-else
                            class="clinic-event-card group border-border bg-card text-card-foreground hover:border-primary/40 relative flex h-full w-full cursor-pointer flex-col overflow-hidden rounded-md border text-left shadow-2xs transition-all select-none hover:shadow-xs"
                            :style="{
                                borderLeftWidth: '4px',
                                borderLeftColor:
                                    event.extendedProps.status === 'paid'
                                        ? '#10b981'
                                        : event.extendedProps.branchColor,
                            }"
                            @click="handleEditAppointment(event.extendedProps)"
                        >
                            <!-- A. Narrow Layout: Used in Week View (< 420px container) -->
                            <div
                                class="clinic-card-narrow flex h-full flex-col justify-between p-1.5 sm:p-2 text-left select-none"
                            >
                                <!-- Top Content Group -->
                                <div class="min-w-0 space-y-1">
                                    <!-- Row 1: Initial Badge + Patient Name + Status Indicator -->
                                    <div class="flex items-center justify-between gap-1 leading-tight">
                                        <div class="flex items-center gap-1 min-w-0 flex-1">
                                            <span
                                                class="size-4 shrink-0 rounded font-bold text-[8px] flex items-center justify-center border"
                                                :class="
                                                    event.extendedProps.status === 'paid'
                                                        ? 'bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800'
                                                        : 'bg-primary/10 text-primary border-primary/20'
                                                "
                                            >
                                                {{ getInitials(event.extendedProps.patientName).slice(0, 1) }}
                                            </span>
                                            <span
                                                class="truncate text-[11px] font-bold text-foreground sm:text-xs"
                                                :title="event.extendedProps.patientName"
                                            >
                                                {{ event.extendedProps.patientName }}
                                            </span>
                                        </div>
                                        <span
                                            class="size-1.5 shrink-0 rounded-full"
                                            :class="
                                                event.extendedProps.status === 'paid'
                                                    ? 'bg-emerald-500'
                                                    : 'bg-amber-500 animate-pulse'
                                            "
                                            :title="
                                                event.extendedProps.status === 'paid'
                                                    ? 'ชำระแล้ว'
                                                    : 'รอออกบิล'
                                            "
                                        />
                                    </div>

                                    <!-- Row 2: Branch Color Dot + Branch Name -->
                                    <div
                                        v-if="selectedBranchId === 'all'"
                                        class="flex items-center gap-1 text-[9px] sm:text-[10px] leading-none"
                                    >
                                        <span
                                            class="size-1.5 rounded-full shrink-0"
                                            :style="{ backgroundColor: event.extendedProps.branchColor }"
                                        />
                                        <span class="truncate font-medium text-muted-foreground">
                                            {{ event.extendedProps.branchName }}
                                        </span>
                                    </div>

                                    <!-- Row 3: Treatment Title -->
                                    <div
                                        class="line-clamp-1 text-[10px] leading-tight font-medium text-foreground/90 sm:text-[11px]"
                                        :title="event.title"
                                    >
                                        {{ event.title }}
                                    </div>

                                    <!-- Row 4: Doctor Name on left + Time on right (Integrated Row!) -->
                                    <div
                                        class="flex items-center justify-between gap-1 text-[9px] text-muted-foreground leading-tight sm:text-[10px]"
                                    >
                                        <span class="truncate">
                                            👨‍⚕️ {{ event.extendedProps.doctorName?.split(' ')[1] || event.extendedProps.doctorName }}
                                        </span>
                                        <span class="font-mono text-[9px] font-medium text-muted-foreground shrink-0">
                                            {{ formatTime(event.start) }}-{{ formatTime(event.end) }}
                                        </span>
                                    </div>
                                </div>

                                <!-- Bottom Section: Price & Action Buttons (Un-wrappable & Pinned) -->
                                <div
                                    class="mt-1 flex items-center justify-between gap-1 border-t border-border/40 pt-1 flex-nowrap shrink-0"
                                >
                                    <span
                                        class="font-mono text-[10px] font-bold text-foreground sm:text-xs truncate shrink-0"
                                    >
                                        ฿{{ event.extendedProps.price?.toLocaleString() }}
                                    </span>

                                    <div class="action-buttons-group flex items-center gap-0.5 shrink-0">
                                        <!-- Quick Edit Button -->
                                        <Button
                                            size="icon-xs"
                                            variant="ghost"
                                            class="h-4.5 w-4.5 rounded text-muted-foreground hover:text-foreground p-0 cursor-pointer shrink-0"
                                            @click.stop="handleEditAppointment(event.extendedProps)"
                                            title="แก้ไขเวลานัดหมาย"
                                        >
                                            <Edit3 class="size-2.5" />
                                        </Button>

                                        <!-- 💳 Billing Button -->
                                        <Button
                                            size="xs"
                                            :variant="event.extendedProps.status === 'paid' ? 'outline' : 'default'"
                                            class="h-4.5 gap-1 px-1.5 text-[9px] font-medium shadow-2xs sm:h-5 sm:text-[10px] cursor-pointer shrink-0"
                                            @click.stop="handleOpenBilling(event.extendedProps)"
                                            :title="event.extendedProps.status === 'paid' ? 'ดูบิลค่ารักษา' : 'ออกบิลค่ารักษา'"
                                        >
                                            <CreditCard class="size-2.5" />
                                            <span class="btn-bill-text hidden xs:inline">{{
                                                event.extendedProps.status === 'paid' ? 'บิล' : 'ออกบิล'
                                            }}</span>
                                        </Button>
                                    </div>
                                </div>
                            </div>

                            <!-- B. Wide Layout: Used in Day View (>= 420px container) -->
                            <div
                                class="clinic-card-wide hidden h-full w-full items-center justify-between gap-3 px-3.5 py-2"
                            >
                                <!-- Section 1: Patient Identity -->
                                <div class="flex items-center gap-3 min-w-[210px] max-w-[280px]">
                                    <div
                                        class="size-9 rounded-full font-bold text-xs flex items-center justify-center shrink-0 border"
                                        :class="
                                            event.extendedProps.status === 'paid'
                                                ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800'
                                                : 'bg-primary/10 text-primary border-primary/20'
                                        "
                                    >
                                        {{ getInitials(event.extendedProps.patientName) }}
                                    </div>
                                    <div class="min-w-0">
                                        <div class="flex items-center gap-2">
                                            <span class="font-bold text-sm text-foreground truncate">
                                                {{ event.extendedProps.patientName }}
                                            </span>
                                            <Badge
                                                :variant="event.extendedProps.status === 'paid' ? 'outline' : 'secondary'"
                                                class="text-[10px] px-1.5 py-0 h-4 shrink-0 font-medium"
                                                :class="
                                                    event.extendedProps.status === 'paid'
                                                        ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5'
                                                        : 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300'
                                                "
                                            >
                                                {{ event.extendedProps.status === 'paid' ? 'ชำระแล้ว' : 'รอออกบิล' }}
                                            </Badge>
                                        </div>
                                        <div class="text-[11px] text-muted-foreground font-mono mt-0.5 flex items-center gap-1">
                                            <Phone class="size-2.5 text-muted-foreground/70" />
                                            <span>{{ event.extendedProps.patientPhone || '08X-XXX-XXXX' }}</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Section 2: Time & Branch -->
                                <div class="flex flex-col gap-1 min-w-[150px]">
                                    <div class="flex items-center gap-1.5 text-xs font-semibold text-foreground font-mono">
                                        <Clock class="size-3.5 text-primary shrink-0" />
                                        <span>{{ formatTime(event.start) }} - {{ formatTime(event.end) }}</span>
                                    </div>
                                    <div class="flex items-center gap-1.5">
                                        <span
                                            class="size-2 rounded-full shrink-0"
                                            :style="{ backgroundColor: event.extendedProps.branchColor }"
                                        />
                                        <span class="text-xs font-medium text-muted-foreground truncate">
                                            {{ event.extendedProps.branchName }}
                                        </span>
                                    </div>
                                </div>

                                <!-- Section 3: Treatment & Doctor -->
                                <div class="flex flex-col gap-0.5 min-w-[180px] flex-1">
                                    <div class="text-xs font-semibold text-foreground line-clamp-1">
                                        {{ event.title }}
                                    </div>
                                    <div class="text-[11px] text-muted-foreground flex items-center gap-1.5">
                                        <span>👨‍⚕️ {{ event.extendedProps.doctorName }}</span>
                                        <span
                                            v-if="event.extendedProps.notes"
                                            class="text-muted-foreground/70 text-[10px] truncate max-w-[220px]"
                                        >
                                            • {{ event.extendedProps.notes }}
                                        </span>
                                    </div>
                                </div>

                                <!-- Section 4: Price & Actions -->
                                <div class="flex items-center gap-3 shrink-0">
                                    <div class="text-right">
                                        <div class="text-[10px] text-muted-foreground">ค่ารักษา</div>
                                        <div class="font-mono text-sm sm:text-base font-bold text-foreground">
                                            ฿{{ event.extendedProps.price?.toLocaleString() }}
                                        </div>
                                    </div>

                                    <div class="flex items-center gap-1.5">
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            class="h-8 px-2.5 text-xs gap-1 border-border shadow-2xs hover:bg-muted cursor-pointer"
                                            @click.stop="handleEditAppointment(event.extendedProps)"
                                        >
                                            <Edit3 class="size-3 text-muted-foreground" />
                                            <span>แก้ไข</span>
                                        </Button>

                                        <Button
                                            size="sm"
                                            :variant="event.extendedProps.status === 'paid' ? 'outline' : 'default'"
                                            class="h-8 px-3 text-xs font-semibold gap-1.5 shadow-2xs cursor-pointer"
                                            :class="
                                                event.extendedProps.status === 'paid'
                                                    ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400'
                                                    : ''
                                            "
                                            @click.stop="handleOpenBilling(event.extendedProps)"
                                        >
                                            <CreditCard class="size-3.5" />
                                            <span>{{ event.extendedProps.status === 'paid' ? 'ดูบิล' : 'ออกบิล' }}</span>
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </article>
                    </template>
                </FullCalendar>
            </CardContent>
        </Card>

        <!-- Feature Guide Footer (Responsive Grid) -->
        <footer
            class="grid grid-cols-1 gap-2.5 pt-1 text-xs sm:grid-cols-2 lg:grid-cols-4"
        >
            <div
                class="bg-card text-muted-foreground flex items-center gap-2 rounded-lg border p-2"
            >
                <Plus class="text-foreground size-3.5 shrink-0" />
                <span class="text-[11px]"
                    ><strong class="text-foreground">เพิ่มนัดหมาย:</strong>
                    กดปุ่มหรือคลิกช่องว่างบนปฏิทิน</span
                >
            </div>
            <div
                class="bg-card text-muted-foreground flex items-center gap-2 rounded-lg border p-2"
            >
                <Filter class="text-foreground size-3.5 shrink-0" />
                <span class="text-[11px]"
                    ><strong class="text-foreground">กรองสาขา:</strong>
                    เลือกสาขาจาก Dropdown ด้านบน</span
                >
            </div>
            <div
                class="bg-card text-muted-foreground flex items-center gap-2 rounded-lg border p-2"
            >
                <Move class="text-foreground size-3.5 shrink-0" />
                <span class="text-[11px]"
                    ><strong class="text-foreground"
                        >ลากวาง (Drag & Drop):</strong
                    >
                    ย้ายเวลาและขยายช่วงตรวจ</span
                >
            </div>
            <div
                class="bg-card text-muted-foreground flex items-center gap-2 rounded-lg border p-2"
            >
                <CreditCard class="text-foreground size-3.5 shrink-0" />
                <span class="text-[11px]"
                    ><strong class="text-foreground">ออกบิลชำระเงิน:</strong>
                    กดปุ่ม "ออกบิล" ข้างใน Event</span
                >
            </div>
        </footer>

        <!-- Modals -->
        <BillingDialog
            v-model:open="isBillingOpen"
            :appointment="selectedBillingAppointment"
            @paid="handleMarkAsPaid"
        />

        <AppointmentFormDialog
            v-model:open="isFormOpen"
            :initial-date="formInitialDate"
            :initial-branch-id="
                selectedBranchId === 'all'
                    ? 'b1'
                    : (selectedBranchId as 'b1' | 'b2' | 'b3')
            "
            :editing-appointment="editingAppointment"
            @save="handleSaveAppointment"
        />
    </div>
</template>

<style>
/* FullCalendar Clinic Master Theme - Seamless Shadcn UI CSS Architecture */
.fullcalendar-clinic-wrapper .fc {
    --fc-border-color: var(--border, #e4e4e7);
    --fc-today-bg-color: var(--accent, rgba(244, 244, 245, 0.4));
    --fc-now-indicator-color: #ef4444;
    --fc-page-bg-color: var(--card, #ffffff);
    --fc-neutral-bg-color: var(--muted, #f4f4f5);
    font-family: inherit;
}

/* 1. Header Toolbar Styling: Authentic Shadcn Button Group & Title */
.fullcalendar-clinic-wrapper .fc-header-toolbar {
    margin-bottom: 1rem !important;
    gap: 0.5rem;
}

.fullcalendar-clinic-wrapper .fc-toolbar-title {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    color: var(--foreground, #09090b);
}

/* Shadcn Button Styling for FullCalendar Native Buttons */
.fullcalendar-clinic-wrapper .fc-button-primary {
    background-color: var(--card, #ffffff) !important;
    color: var(--foreground, #09090b) !important;
    border: 1px solid var(--border, #e4e4e7) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.65rem !important;
    border-radius: 0.375rem !important;
    text-transform: capitalize !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04) !important;
    transition: all 0.15s ease-in-out !important;
}

.fullcalendar-clinic-wrapper .fc-button-primary:hover {
    background-color: var(--muted, #f4f4f5) !important;
    color: var(--foreground, #09090b) !important;
}

.fullcalendar-clinic-wrapper .fc-button-primary:focus {
    box-shadow: 0 0 0 2px var(--background, #ffffff), 0 0 0 4px var(--ring, #18181b) !important;
}

.fullcalendar-clinic-wrapper .fc-button-primary.fc-button-active {
    background-color: var(--primary, #09090b) !important;
    color: var(--primary-foreground, #ffffff) !important;
    border-color: var(--primary, #09090b) !important;
    font-weight: 600 !important;
}

.fullcalendar-clinic-wrapper .fc-button-primary:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}

/* Button group radius */
.fullcalendar-clinic-wrapper .fc-button-group > .fc-button:not(:last-child) {
    border-top-right-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
}

.fullcalendar-clinic-wrapper .fc-button-group > .fc-button:not(:first-child) {
    border-top-left-radius: 0 !important;
    border-bottom-left-radius: 0 !important;
    margin-left: -1px !important;
}

/* 2. Responsive Toolbar on Small Viewports (Mobile < 640px) */
@media (max-width: 640px) {
    .fullcalendar-clinic-wrapper .fc-header-toolbar {
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 0.625rem !important;
    }

    .fullcalendar-clinic-wrapper .fc-toolbar-chunk {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
    }

    /* Put title at the top row */
    .fullcalendar-clinic-wrapper .fc-toolbar-chunk:nth-child(2) {
        order: -1 !important;
        justify-content: center !important;
    }

    .fullcalendar-clinic-wrapper .fc-toolbar-title {
        font-size: 1rem !important;
        text-align: center !important;
    }

    .fullcalendar-clinic-wrapper .fc-button {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.75rem !important;
    }
}

/* 3. Table Header & Column Styling */
.fullcalendar-clinic-wrapper .fc-theme-standard td,
.fullcalendar-clinic-wrapper .fc-theme-standard th {
    border-color: var(--border, #e4e4e7) !important;
}

.fullcalendar-clinic-wrapper .fc-col-header-cell {
    background-color: var(--card, #ffffff);
    padding: 6px 0 !important;
}

.fullcalendar-clinic-wrapper .fc-col-header-cell-cushion {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: var(--foreground, #09090b) !important;
    text-decoration: none !important;
}

/* Time axis and slot labels */
.fullcalendar-clinic-wrapper .fc-timegrid-axis-cushion,
.fullcalendar-clinic-wrapper .fc-timegrid-slot-label-cushion {
    font-family: monospace;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    color: var(--muted-foreground, #71717a) !important;
}

.fullcalendar-clinic-wrapper .fc-col-header-cell {
    background-color: var(--card, #ffffff);
    padding: 8px 0 !important;
    min-width: 140px;
}

.fullcalendar-clinic-wrapper .fc-timegrid-col {
    min-width: 140px;
}

.fullcalendar-clinic-wrapper .fc-col-header-cell-cushion {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: var(--foreground, #09090b) !important;
    text-decoration: none !important;
}

/* Time axis and slot labels */
.fullcalendar-clinic-wrapper .fc-timegrid-axis-cushion,
.fullcalendar-clinic-wrapper .fc-timegrid-slot-label-cushion {
    font-family: monospace;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    color: var(--muted-foreground, #71717a) !important;
}

.fullcalendar-clinic-wrapper .fc-timegrid-slot {
    height: 60px !important;
    border-bottom: 1px solid var(--border, #e4e4e7) !important;
}

.fullcalendar-clinic-wrapper .fc-timegrid-slot-minor {
    border-top-style: dotted !important;
    border-top-color: var(--border, #e4e4e7) !important;
    opacity: 0.6;
}

/* 4. Event Shell: Transparent wrapper allowing custom Shadcn card to render cleanly */
.fullcalendar-clinic-wrapper .fc-timegrid-event-harness {
    margin: 1px 2px !important;
}

.fullcalendar-clinic-wrapper .fc-event {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    border-radius: 0.375rem !important;
    overflow: visible !important;
}

.fullcalendar-clinic-wrapper .fc-event-main {
    padding: 0 !important;
    height: 100%;
}

/* Container Queries for Responsive Event Cards in TimeGrid */
.fullcalendar-clinic-wrapper .fc-timegrid-event {
    container-type: inline-size;
}

/* Default (Narrow view / Week view): show narrow vertical card, hide wide card */
.clinic-card-wide {
    display: none !important;
}

.clinic-card-narrow {
    display: flex !important;
}

/* Wide Container (e.g. Day View >= 420px): show rich horizontal clinic ticket */
@container (min-width: 420px) {
    .clinic-card-narrow {
        display: none !important;
    }
    .clinic-card-wide {
        display: flex !important;
    }
}

@container (max-width: 140px) {
    .clinic-card-narrow .btn-bill-text {
        display: none !important;
    }
}

@container (max-width: 80px) {
    .clinic-card-narrow .action-buttons-group {
        display: none !important;
    }
}

/* Month View Styling: Compact Shadcn Event Chips */
.fullcalendar-clinic-wrapper .fc-daygrid-event {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 1px 2px !important;
    margin: 1px 0 !important;
}

.fullcalendar-clinic-wrapper .fc-daygrid-event-harness {
    margin: 1px 0 !important;
}

.fullcalendar-clinic-wrapper .fc-daygrid-dot-event {
    background: transparent !important;
}

.fullcalendar-clinic-wrapper .clinic-month-pill {
    max-width: 100%;
}

/* 5. Live Now Indicator */
.fullcalendar-clinic-wrapper .fc-timegrid-now-indicator-line {
    border-color: #ef4444 !important;
    border-width: 2px !important;
    z-index: 10;
}

.fullcalendar-clinic-wrapper .fc-timegrid-now-indicator-arrow {
    border-color: #ef4444 !important;
    border-bottom-color: transparent !important;
    border-top-color: transparent !important;
}

/* Smooth mobile touch scrolling */
.fullcalendar-clinic-wrapper .fc-scroller {
    -webkit-overflow-scrolling: touch;
}

.fullcalendar-clinic-wrapper .fc-scroller::-webkit-scrollbar {
    height: 5px;
    width: 5px;
}

.fullcalendar-clinic-wrapper .fc-scroller::-webkit-scrollbar-thumb {
    background-color: var(--border, #e4e4e7);
    border-radius: 9999px;
}
</style>
