import java.io.File;
import java.util.HashSet;
import java.util.Set;
import org.jf.dexlib2.Opcodes;
import org.jf.dexlib2.dexbacked.DexBackedDexFile;
import org.jf.dexlib2.writer.io.FileDataStore;
import org.jf.dexlib2.writer.pool.DexPool;

/** Merge: all classes from base.dex except those also defined in patch.dex,
 *  then all classes from patch.dex. Outputs merged dex. Pure dexlib2. */
public class DexMerge {
    public static void main(String[] args) throws Exception {
        String base = args[0], patch = args[1], out = args[2];
        DexBackedDexFile baseDex = DexBackedDexFile.fromInputStream(
            Opcodes.getDefault(), new java.io.BufferedInputStream(new java.io.FileInputStream(base)));
        DexBackedDexFile patchDex = DexBackedDexFile.fromInputStream(
            Opcodes.getDefault(), new java.io.BufferedInputStream(new java.io.FileInputStream(patch)));
        Set<String> patched = new HashSet<String>();
        for (org.jf.dexlib2.iface.ClassDef c : patchDex.getClasses()) {
            patched.add(c.getType());
        }
        DexPool pool = new DexPool(Opcodes.getDefault());
        int kept = 0, replaced = 0;
        for (org.jf.dexlib2.iface.ClassDef c : baseDex.getClasses()) {
            if (patched.contains(c.getType())) { replaced++; continue; }
            pool.internClass(c); kept++;
        }
        for (org.jf.dexlib2.iface.ClassDef c : patchDex.getClasses()) {
            pool.internClass(c);
        }
        pool.writeTo(new FileDataStore(new File(out)));
        System.out.println("kept=" + kept + " replaced=" + replaced + " patched=" + patched.size());
    }
}
