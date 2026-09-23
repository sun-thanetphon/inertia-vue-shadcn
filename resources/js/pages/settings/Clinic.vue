<script setup lang="ts">
import { Head } from '@inertiajs/vue3';
import {
    Building2,
    CalendarClock,
    CheckCircle2,
    FileText,
    Mail,
    MapPin,
    Phone,
    Save,
    Sparkles,
} from '@lucide/vue';
import { ref } from 'vue';
import { toast } from 'vue-sonner';
import Heading from '@/components/Heading.vue';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { edit as editClinic } from '@/routes/clinic';

defineOptions({
    layout: {
        breadcrumbs: [
            {
                title: 'Clinic settings',
                href: editClinic(),
            },
        ],
    },
});

// Form state variables following strict camelCase (RULE-NAMING-01)
const clinicNameTh = ref('คลินิกเวชกรรม สุขภาพดี');
const clinicNameEn = ref('Sukkapapdee Medical Clinic');
const licenseNumber = ref('MD-101030045/2567');
const taxId = ref('0105566012345');

const phoneNumber = ref('02-999-8888');
const emailAddress = ref('contact@sukkapapdee.clinic');
const addressDetail = ref('99/45 ถนนพหลโยธิน แขวงลาดยาว เขตจตุจักร กรุงเทพฯ 10900');

const openingTime = ref('09:00');
const closingTime = ref('20:00');
const slotInterval = ref('30');
const autoReadCard = ref(true);
const requireSignature = ref(true);
const isSaving = ref(false);

const handleSaveSettings = () => {
    isSaving.value = true;
    setTimeout(() => {
        isSaving.value = false;
        toast.success('บันทึกข้อมูลการตั้งค่าคลินิกเรียบร้อยแล้ว (POC)');
    }, 600);
};
</script>

<template>
    <Head title="Clinic settings" />

    <h1 class="sr-only">Clinic settings</h1>

    <div class="space-y-6">
        <div class="flex items-center justify-between">
            <Heading
                variant="small"
                title="Clinic Settings"
                description="จัดการข้อมูลสถานพยาบาล ใบอนุญาต และการตั้งค่าระบบการทำงานของคลินิก"
            />
            <Badge variant="outline" class="gap-1 border-primary/40 text-primary">
                <Sparkles class="size-3" />
                PoC Extension
            </Badge>
        </div>

        <form class="space-y-6" @submit.prevent="handleSaveSettings">
            <!-- 1. ข้อมูลทั่วไปและใบอนุญาตสถานพยาบาล -->
            <Card>
                <CardHeader>
                    <CardTitle class="flex items-center gap-2 text-base font-medium">
                        <Building2 class="size-4 text-primary" />
                        ข้อมูลทั่วไปสถานพยาบาล (General Information)
                    </CardTitle>
                    <CardDescription>
                        ข้อมูลชื่อคลินิกและเลขที่ใบอนุญาตสำหรับใช้พิมพ์บนใบเสร็จและเวชระเบียน
                    </CardDescription>
                </CardHeader>

                <CardContent class="space-y-4">
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div class="space-y-2">
                            <Label for="clinicNameTh">ชื่อคลินิก (ภาษาไทย)</Label>
                            <Input
                                id="clinicNameTh"
                                v-model="clinicNameTh"
                                placeholder="เช่น คลินิกเวชกรรม สุขภาพดี"
                                required
                            />
                        </div>

                        <div class="space-y-2">
                            <Label for="clinicNameEn">Clinic Name (English)</Label>
                            <Input
                                id="clinicNameEn"
                                v-model="clinicNameEn"
                                placeholder="e.g. Sukkapapdee Medical Clinic"
                            />
                        </div>
                    </div>

                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div class="space-y-2">
                            <Label for="licenseNumber">เลขที่ใบอนุญาตประกอบกิจการสถานพยาบาล</Label>
                            <div class="relative">
                                <FileText class="absolute top-2.5 left-3 size-4 text-muted-foreground" />
                                <Input
                                    id="licenseNumber"
                                    v-model="licenseNumber"
                                    class="pl-9"
                                    placeholder="เช่น 101030045/2567"
                                    required
                                />
                            </div>
                        </div>

                        <div class="space-y-2">
                            <Label for="taxId">เลขประจำตัวผู้เสียภาษี (Tax ID)</Label>
                            <Input
                                id="taxId"
                                v-model="taxId"
                                placeholder="เช่น 0105566012345"
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

            <!-- 2. ข้อมูลการติดต่อและสถานที่ตั้ง -->
            <Card>
                <CardHeader>
                    <CardTitle class="flex items-center gap-2 text-base font-medium">
                        <MapPin class="size-4 text-primary" />
                        สถานที่ตั้งและการติดต่อ (Contact & Location)
                    </CardTitle>
                    <CardDescription>
                        ข้อมูลที่อยู่และช่องทางติดต่อที่จะปรากฏในใบรับรองแพทย์และเอกสารทางการ
                    </CardDescription>
                </CardHeader>

                <CardContent class="space-y-4">
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div class="space-y-2">
                            <Label for="phoneNumber">เบอร์โทรศัพท์คลินิก</Label>
                            <div class="relative">
                                <Phone class="absolute top-2.5 left-3 size-4 text-muted-foreground" />
                                <Input
                                    id="phoneNumber"
                                    v-model="phoneNumber"
                                    class="pl-9"
                                    placeholder="02-xxx-xxxx หรือ 08x-xxx-xxxx"
                                />
                            </div>
                        </div>

                        <div class="space-y-2">
                            <Label for="emailAddress">อีเมลติดต่อ</Label>
                            <div class="relative">
                                <Mail class="absolute top-2.5 left-3 size-4 text-muted-foreground" />
                                <Input
                                    id="emailAddress"
                                    v-model="emailAddress"
                                    type="email"
                                    class="pl-9"
                                    placeholder="contact@clinic.com"
                                />
                            </div>
                        </div>
                    </div>

                    <div class="space-y-2">
                        <Label for="addressDetail">ที่อยู่สถานพยาบาล</Label>
                        <Input
                            id="addressDetail"
                            v-model="addressDetail"
                            placeholder="บ้านเลขที่ อาคาร ถนน แขวง/ตำบล เขต/อำเภอ จังหวัด"
                        />
                    </div>
                </CardContent>
            </Card>

            <!-- 3. การตั้งค่าระบบและการทำงาน (Operations & Hardware) -->
            <Card>
                <CardHeader>
                    <CardTitle class="flex items-center gap-2 text-base font-medium">
                        <CalendarClock class="size-4 text-primary" />
                        ระบบนัดหมายและฮาร์ดแวร์ (Operations & Devices)
                    </CardTitle>
                    <CardDescription>
                        กำหนดเวลาทำการ และคุณสมบัติการเชื่อมต่อกับเครื่องอ่านบัตร/ลายเซ็นดิจิทัล
                    </CardDescription>
                </CardHeader>

                <CardContent class="space-y-5">
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div class="space-y-2">
                            <Label for="openingTime">เวลาเปิดทำการ</Label>
                            <Input
                                id="openingTime"
                                v-model="openingTime"
                                type="time"
                            />
                        </div>

                        <div class="space-y-2">
                            <Label for="closingTime">เวลาปิดทำการ</Label>
                            <Input
                                id="closingTime"
                                v-model="closingTime"
                                type="time"
                            />
                        </div>

                        <div class="space-y-2">
                            <Label for="slotInterval">ช่องเวลาตารางนัด (นาที)</Label>
                            <Select v-model="slotInterval">
                                <SelectTrigger id="slotInterval">
                                    <SelectValue placeholder="เลือกระยะเวลา" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="15">15 นาที / คิว</SelectItem>
                                    <SelectItem value="30">30 นาที / คิว</SelectItem>
                                    <SelectItem value="45">45 นาที / คิว</SelectItem>
                                    <SelectItem value="60">60 นาที / คิว</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <Separator />

                    <div class="space-y-3">
                        <div class="flex items-start space-x-3 rounded-md border p-3 bg-muted/20">
                            <Checkbox
                                id="autoReadCard"
                                :model-value="autoReadCard"
                                @update:model-value="(val) => autoReadCard = val === true"
                            />
                            <div class="space-y-1 leading-none">
                                <Label for="autoReadCard" class="cursor-pointer font-medium">
                                    เปิดใช้งานระบบอ่านบัตรประชาชนอัตโนมัติ (Smart Card Auto-Detection)
                                </Label>
                                <p class="text-xs text-muted-foreground">
                                    เมื่อเสียบบัตรประชาชนเข้ากับเครื่องอ่าน ระบบจะดึงข้อมูลประวัติผู้ป่วยขึ้นหน้าต่างโดยอัตโนมัติ
                                </p>
                            </div>
                        </div>

                        <div class="flex items-start space-x-3 rounded-md border p-3 bg-muted/20">
                            <Checkbox
                                id="requireSignature"
                                :model-value="requireSignature"
                                @update:model-value="(val) => requireSignature = val === true"
                            />
                            <div class="space-y-1 leading-none">
                                <Label for="requireSignature" class="cursor-pointer font-medium">
                                    บังคับใช้ระบบลายเซ็นดิจิทัลในใบยินยอม (Digital Consent Signature)
                                </Label>
                                <p class="text-xs text-muted-foreground">
                                    เปิดใช้งานแท็บเล็ตหรือ Signature Pad สำหรับเซ็นเอกสารยินยอมรับการรักษา
                                </p>
                            </div>
                        </div>
                    </div>
                </CardContent>

                <CardFooter class="flex items-center justify-between border-t bg-muted/10 px-6 py-4">
                    <span class="text-xs text-muted-foreground flex items-center gap-1.5">
                        <CheckCircle2 class="size-3.5 text-emerald-500" />
                        ระบบจะบันทึกการตั้งค่าแยกตามสาขาคลินิก
                    </span>
                    <Button type="submit" :disabled="isSaving" class="gap-2">
                        <Save class="size-4" />
                        {{ isSaving ? 'กำลังบันทึก...' : 'บันทึกการตั้งค่า' }}
                    </Button>
                </CardFooter>
            </Card>
        </form>
    </div>
</template>
