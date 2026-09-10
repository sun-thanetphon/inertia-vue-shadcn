<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        if (User::count() === 0) {
            User::factory(99)->create();
        }

        $role = Role::firstOrCreate(['name' => 'writer']);
        $edit = Permission::firstOrCreate(['name' => 'edit articles']);
        $add = Permission::firstOrCreate(['name' => 'add articles']);
        $view = Permission::firstOrCreate(['name' => 'view articles']);

        $user = User::firstOrCreate(
            ['email' => 'test@mail.com'],
            [
                'name' => 'Test User',
                'password' => bcrypt('password')
            ]
        );

        $role->syncPermissions([$edit, $add, $view]);

        if (!$user->hasRole($role)) {
            $user->assignRole($role);
        }
    }
}
