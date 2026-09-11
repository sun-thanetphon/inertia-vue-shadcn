<script setup lang="ts">
import { ref, watch } from 'vue';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { toast } from 'vue-sonner';
import { CalendarPlus, Clock, Stethoscope, User } from '@lucide/vue';
import type { Appointment } from './mockData';
import { clinicBranches, clinicDoctors, treatmentOptions } from './mockData';

const props = defineProps<{
    open: boolean;
    initialDate?: string;
    initialBranchId?: 'b1' | 'b2' | 'b3';
    editingAppointment?: Appointment | null;
}>();

const emit = defineEmits<{
    (e: 'update:open', value: boolean): void;
    (e: 'save', appointment: Appointment): void;
}>();

const form = ref({
    patientName: '',
    patientPhone: '',
    branchId: 'b1' as 'b1' | 'b2' | 'b3',
    doctorName: clinicDoctors[0].name,
    treatment: treatmentOptions[0].name,
    price: treatmentOptions[0].price,
    start: '',
    end: '',
    notes: '',
});

watch(
    () => props.open,
    (isOpen) => {
        if (isOpen) {
            if (props.editingAppointment) {
                // Editing mode
                form.value = {
                    patientName: props.editingAppointment.patientName,
                    patientPhone: props.editingAppointment.patientPhone,
                    branchId: props.editingAppointment.branchId,
                    doctorName: props.editingAppointment.doctorName,
                    treatment: props.editingAppointment.treatment,
                    price: props.editingAppointment.price,
                    start: props.editingAppointment.start.slice(0, 16),
                    end: props.editingAppointment.end.slice(0, 16),
                    notes: props.editingAppointment.notes || '',
                };
            } else {
                // New appointment mode
                const defaultDate = props.initialDate || new Date().toISOString().split('T')[0];
                form.value = {
                    patientName: '',
                    patientPhone: '',
                    branchId: props.initialBranchId || 'b1',
                    doctorName: clinicDoctors[0].name,
                    treatment: treatmentOptions[0].name,
                    price: treatmentOptions[0].price,
                    start: `${defaultDate}T09:00`,
                    end: `${defaultDate}T10:00`,
                    notes: '',
                };
            }
        }
    }
);

function onTreatmentChange(treatmentName: string) {
    form.value.treatment = treatmentName;
    const match = treatmentOptions.find((t) => t.name === treatmentName);
    if (match) {
        form.value.price = match.price;
    }
}

function handleSave() {
    if (!form.value.patientName.trim()) {
        toast.error('กรุณากรอกชื่อคนไข้');
        return;
    }
    if (!form.value.start || !form.value.end) {
        toast.error('กรุณาระบุวันและเวลา');
        return;
    }

    const appointment: Appointment = {
        id: props.editingAppointment ? props.editingAppointment.id : `apt-${Date.now()}`,
        title: form.value.treatment.split(' (')[0],
        start: form.value.start.includes(':00', 14) ? form.value.start : `${form.value.start}:00`,
        end: form.value.end.includes(':00', 14) ? form.value.end : `${form.value.end}:00`,
        branchId: form.value.branchId,
        patientName: form.value.patientName,
        patientPhone: form.value.patientPhone || '08X-XXX-XXXX',
        doctorName: form.value.doctorName,
        treatment: form.value.treatment,
        price: form.value.price,
        status: props.editingAppointment ? props.editingAppointment.status : 'pending_bill',
        notes: form.value.notes,
    };

    emit('save', appointment);
    toast.success(props.editingAppointment ? 'แก้ไขนัดหมายสำเร็จ' : 'เพิ่มนัดหมายใหม่สำเร็จ', {
        description: `คนไข้: ${appointment.patientName} (${appointment.treatment})`
    });
    emit('update:open', false);
}
</script>

<template>
    <Dialog :open="open" @update:open="(val) => emit('update:open', val)">
        <DialogContent class="sm:max-w-[500px]">
            <DialogHeader>
                <DialogTitle class="flex items-center gap-2 text-lg font-bold">
                    <CalendarPlus class="size-5 text-primary" />
                    {{ editingAppointment ? 'แก้ไขนัดหมาย' : 'เพิ่มนัดหมายคลินิกใหม่' }}
                </DialogTitle>
                <DialogDescription>
                    กรอกข้อมูลคนไข้และเลือกแพทย์ผู้ตรวจ พร้อมกำหนดวันเวลา
                </DialogDescription>
            </DialogHeader>

            <form @submit.prevent="handleSave" class="space-y-3.5 py-2">
                <!-- Patient Name & Phone -->
                <div class="grid grid-cols-2 gap-3">
                    <div class="space-y-1.5">
                        <Label for="patientName" class="text-xs">ชื่อ-นามสกุล คนไข้ *</Label>
                        <Input
                            id="patientName"
                            v-model="form.patientName"
                            placeholder="เช่น นาย สมชาย ใจดี"
                            required
                        />
                    </div>
                    <div class="space-y-1.5">
                        <Label for="patientPhone" class="text-xs">เบอร์โทรศัพท์</Label>
                        <Input
                            id="patientPhone"
                            v-model="form.patientPhone"
                            placeholder="081-234-5678"
                        />
                    </div>
                </div>

                <!-- Branch & Doctor -->
                <div class="grid grid-cols-2 gap-3">
                    <div class="space-y-1.5">
                        <Label class="text-xs">สาขาคลินิก *</Label>
                        <Select v-model="form.branchId">
                            <SelectTrigger>
                                <SelectValue placeholder="เลือกสาขา" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem
                                    v-for="b in clinicBranches"
                                    :key="b.id"
                                    :value="b.id"
                                >
                                    {{ b.name }}
                                </SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div class="space-y-1.5">
                        <Label class="text-xs">แพทย์ผู้ตรวจ *</Label>
                        <Select v-model="form.doctorName">
                            <SelectTrigger>
                                <SelectValue placeholder="เลือกแพทย์" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem
                                    v-for="d in clinicDoctors"
                                    :key="d.id"
                                    :value="d.name"
                                >
                                    {{ d.name }}
                                </SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                <!-- Treatment & Price -->
                <div class="space-y-1.5">
                    <Label class="text-xs">บริการ / การรักษา *</Label>
                    <Select :model-value="form.treatment" @update:model-value="onTreatmentChange">
                        <SelectTrigger>
                            <SelectValue placeholder="เลือกการรักษา" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem
                                v-for="t in treatmentOptions"
                                :key="t.name"
                                :value="t.name"
                            >
                                {{ t.name }} (฿{{ t.price.toLocaleString() }})
                            </SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <!-- Start & End Time -->
                <div class="grid grid-cols-2 gap-3">
                    <div class="space-y-1.5">
                        <Label for="startTime" class="text-xs">เวลาเริ่มต้น *</Label>
                        <Input
                            id="startTime"
                            type="datetime-local"
                            v-model="form.start"
                            required
                        />
                    </div>
                    <div class="space-y-1.5">
                        <Label for="endTime" class="text-xs">เวลาสิ้นสุด *</Label>
                        <Input
                            id="endTime"
                            type="datetime-local"
                            v-model="form.end"
                            required
                        />
                    </div>
                </div>

                <!-- Notes -->
                <div class="space-y-1.5">
                    <Label for="notes" class="text-xs">หมายเหตุเพิ่มเติม</Label>
                    <Input
                        id="notes"
                        v-model="form.notes"
                        placeholder="เช่น คนไข้มีประวัติแพ้ยา หรือต้องการตรวจพิเศษ"
                    />
                </div>

                <DialogFooter class="pt-2">
                    <Button type="button" variant="outline" size="sm" @click="emit('update:open', false)">
                        ยกเลิก
                    </Button>
                    <Button type="submit" size="sm" class="bg-primary text-primary-foreground font-semibold">
                        {{ editingAppointment ? 'บันทึกการแก้ไข' : 'ยืนยันเพิ่มนัดหมาย' }}
                    </Button>
                </DialogFooter>
            </form>
        </DialogContent>
    </Dialog>
</template>
