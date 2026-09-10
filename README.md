# inertia-vue-shadcn

# คู่มือสำหรับ Inertia.js + laravel starter kit shadcn

[ลิงค์ Youtube สำหรับอ้างอิง](https://youtu.be/iLmq2zpfRI4?si=QCxR1CIispZ5K8nM)

## File สำคัญ

```bash
AppSidebar.vue = สำหรับเพิ่มเมนูใหม่
```

## Usage

```python
php artisan make:controller UserController --resource

Route::resource('/users', UserController::class); //ใช้สำหรับเพิ่มเมนูใหม่


class UserController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $users = User::paginate(10);
        return Inertia::render('Users/Index', [
            'users' => $users,
        ]);
    }

}

```

## Contributing

สร้าง Folder/path ตามนี้

```
/Users/esper/Desktop/RD/my-app-shadcn-vue/resources/js/pages/Users/Index.vue
```

- ตัวอย่างสำหรับการทำตาราง + Paginate อยู่ใน User/Index
- ตัวอย่างสำหรับการดึง auth detail อยู่ใน dashboard

## หากต้องการส่ง attributes ต่างๆเข้ามาที่ Vue

```
ให้ส่งผ่าน File HandleInertiaRequests ใน middleware
```
