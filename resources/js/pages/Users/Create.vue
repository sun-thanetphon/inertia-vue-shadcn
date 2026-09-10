<script setup lang="ts">
import { Head, Link, router } from "@inertiajs/vue3";
import { toTypedSchema } from "@vee-validate/zod";
import { useForm } from "vee-validate";
import * as z from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import {
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";

const formSchema = toTypedSchema(
    z.object({
        name: z
            .string()
            .min(2, "Name must be at least 2 characters")
            .max(255, "Name must not exceed 255 characters"),

        email: z.string().email("Please enter a valid email address"),

        password: z.string().min(8, "Password must be at least 8 characters"),

        image: z.instanceof(File).nullable().optional(),
    }),
);

const form = useForm({
    validationSchema: formSchema,
});

const onSubmit = form.handleSubmit((values) => {
    const data = new FormData();

    data.append("name", values.name);
    data.append("email", values.email);
    data.append("password", values.password);

    if (values.image) {
        data.append("image", values.image);
    }

    router.post("/users", data, {
        forceFormData: true,
        preserveScroll: true,
    });
});

defineOptions({
    layout: {
        breadcrumbs: [
            {
                title: "User",
                href: "/users",
            },
            {
                title: "Create",
                href: "/users/create",
            },
        ],
    },
});
</script>

<template>
    <Head title="Create User" />

    <div class="p-6">
        <Button as-child variant="outline" class="mb-6">
            <Link href="/users"> Back </Link>
        </Button>

        <div class="max-w-xl">
            <h1 class="mb-6 text-2xl font-semibold">Create User</h1>

            <form class="space-y-6" @submit="onSubmit">
                <!-- Name -->
                <FormField v-slot="{ componentField }" name="name">
                    <FormItem>
                        <FormLabel>Name</FormLabel>

                        <FormControl>
                            <Input
                                type="text"
                                placeholder="John Doe"
                                v-bind="componentField"
                            />
                        </FormControl>

                        <FormMessage />
                    </FormItem>
                </FormField>

                <!-- Email -->
                <FormField v-slot="{ componentField }" name="email">
                    <FormItem>
                        <FormLabel>Email</FormLabel>

                        <FormControl>
                            <Input
                                type="email"
                                placeholder="john@example.com"
                                v-bind="componentField"
                            />
                        </FormControl>

                        <FormMessage />
                    </FormItem>
                </FormField>

                <!-- Password -->
                <FormField v-slot="{ componentField }" name="password">
                    <FormItem>
                        <FormLabel>Password</FormLabel>

                        <FormControl>
                            <Input
                                type="password"
                                placeholder="********"
                                v-bind="componentField"
                            />
                        </FormControl>

                        <FormMessage />
                    </FormItem>
                </FormField>

                <!-- Image -->
                <FormField name="image">
                    <FormItem>
                        <FormLabel>Profile Image</FormLabel>

                        <FormControl>
                            <Input
                                type="file"
                                accept="image/*"
                                @change="
                                    (event) => {
                                        const target =
                                            event.target as HTMLInputElement;

                                        form.setFieldValue(
                                            'image',
                                            target.files?.[0] ?? null,
                                        );
                                    }
                                "
                            />
                        </FormControl>

                        <FormMessage />
                    </FormItem>
                </FormField>

                <!-- Submit -->
                <div class="flex gap-2">
                    <Button type="submit" :disabled="form.isSubmitting">
                        {{ form.isSubmitting ? "Creating..." : "Create User" }}
                    </Button>

                    <Button as-child type="button" variant="outline">
                        <Link href="/users"> Cancel </Link>
                    </Button>
                </div>
            </form>
        </div>
    </div>
</template>
