; ModuleID = 'mycomplex.c'
source_filename = "mycomplex.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

%struct.Complex = type { double, double }

@__const.main.z1 = private unnamed_addr constant %struct.Complex { double 3.000000e+00, double 4.000000e+00 }, align 8
@__const.main.z2 = private unnamed_addr constant %struct.Complex { double 1.000000e+00, double 2.000000e+00 }, align 8

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @mul(ptr dead_on_unwind noalias writable sret(%struct.Complex) align 8 %0, ptr dead_on_return noundef %1, ptr dead_on_return noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  store ptr %0, ptr %4, align 8
  store ptr %2, ptr %5, align 8
  store ptr %1, ptr %6, align 8
  %7 = getelementptr inbounds nuw %struct.Complex, ptr %1, i32 0, i32 0
  %8 = load double, ptr %7, align 8
  %9 = getelementptr inbounds nuw %struct.Complex, ptr %2, i32 0, i32 0
  %10 = load double, ptr %9, align 8
  %11 = getelementptr inbounds nuw %struct.Complex, ptr %1, i32 0, i32 1
  %12 = load double, ptr %11, align 8
  %13 = getelementptr inbounds nuw %struct.Complex, ptr %2, i32 0, i32 1
  %14 = load double, ptr %13, align 8
  %15 = fmul double %12, %14
  %16 = fneg double %15
  %17 = call double @llvm.fmuladd.f64(double %8, double %10, double %16)
  %18 = getelementptr inbounds nuw %struct.Complex, ptr %0, i32 0, i32 0
  store double %17, ptr %18, align 8
  %19 = getelementptr inbounds nuw %struct.Complex, ptr %1, i32 0, i32 0
  %20 = load double, ptr %19, align 8
  %21 = getelementptr inbounds nuw %struct.Complex, ptr %2, i32 0, i32 1
  %22 = load double, ptr %21, align 8
  %23 = getelementptr inbounds nuw %struct.Complex, ptr %1, i32 0, i32 1
  %24 = load double, ptr %23, align 8
  %25 = getelementptr inbounds nuw %struct.Complex, ptr %2, i32 0, i32 0
  %26 = load double, ptr %25, align 8
  %27 = fmul double %24, %26
  %28 = call double @llvm.fmuladd.f64(double %20, double %22, double %27)
  %29 = getelementptr inbounds nuw %struct.Complex, ptr %0, i32 0, i32 1
  store double %28, ptr %29, align 8
  ret void
}

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fmuladd.f64(double, double, double) #1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local void @add(ptr dead_on_unwind noalias writable sret(%struct.Complex) align 8 %0, ptr dead_on_return noundef %1, ptr dead_on_return noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  store ptr %0, ptr %4, align 8
  store ptr %2, ptr %5, align 8
  store ptr %1, ptr %6, align 8
  %7 = getelementptr inbounds nuw %struct.Complex, ptr %1, i32 0, i32 0
  %8 = load double, ptr %7, align 8
  %9 = getelementptr inbounds nuw %struct.Complex, ptr %2, i32 0, i32 0
  %10 = load double, ptr %9, align 8
  %11 = fadd double %8, %10
  %12 = getelementptr inbounds nuw %struct.Complex, ptr %0, i32 0, i32 0
  store double %11, ptr %12, align 8
  %13 = getelementptr inbounds nuw %struct.Complex, ptr %1, i32 0, i32 1
  %14 = load double, ptr %13, align 8
  %15 = getelementptr inbounds nuw %struct.Complex, ptr %2, i32 0, i32 1
  %16 = load double, ptr %15, align 8
  %17 = fadd double %14, %16
  %18 = getelementptr inbounds nuw %struct.Complex, ptr %0, i32 0, i32 1
  store double %17, ptr %18, align 8
  ret void
}

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca %struct.Complex, align 8
  %3 = alloca %struct.Complex, align 8
  %4 = alloca %struct.Complex, align 8
  %5 = alloca %struct.Complex, align 8
  %6 = alloca %struct.Complex, align 8
  %7 = alloca %struct.Complex, align 8
  %8 = alloca %struct.Complex, align 8
  store i32 0, ptr %1, align 4
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %2, ptr align 8 @__const.main.z1, i64 16, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %3, ptr align 8 @__const.main.z2, i64 16, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %6, ptr align 8 %2, i64 16, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %7, ptr align 8 %3, i64 16, i1 false)
  call void @mul(ptr dead_on_unwind writable sret(%struct.Complex) align 8 %5, ptr dead_on_return noundef %6, ptr dead_on_return noundef %7)
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %8, ptr align 8 %2, i64 16, i1 false)
  call void @add(ptr dead_on_unwind writable sret(%struct.Complex) align 8 %4, ptr dead_on_return noundef %5, ptr dead_on_return noundef %8)
  ret i32 0
}

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias writeonly captures(none), ptr noalias readonly captures(none), i64, i1 immarg) #2

attributes #0 = { noinline nounwind optnone uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5, !6}
!llvm.ident = !{!7}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "clang version 22.1.5 (https://github.com/llvm/llvm-project 5ea218a153f4d2f815b8244eab3e4b4ba5e00e6c)", isOptimized: false, runtimeVersion: 0, emissionKind: NoDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "mycomplex.c", directory: "c:\\Master_Bear\\3_kyrs\\6_semestr\\teor_formal_az_kommpilitorov\\lb5\\AST")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 1, !"wchar_size", i32 2}
!4 = !{i32 8, !"PIC Level", i32 2}
!5 = !{i32 7, !"uwtable", i32 2}
!6 = !{i32 1, !"MaxTLSAlign", i32 65536}
!7 = !{!"clang version 22.1.5 (https://github.com/llvm/llvm-project 5ea218a153f4d2f815b8244eab3e4b4ba5e00e6c)"}
